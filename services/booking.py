from fastapi import HTTPException
import random
import string
from datetime import datetime, timezone
from types import SimpleNamespace
from db.supabase import supabase
from models.models import fullregistration, Reservation, Customer
from .emailbox import email_pending, email_confirmed, email_cancelled


def generate_unique_code(supabase, length=10):
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        response = supabase.table("reservation") \
            .select("transaction_code") \
            .eq("transaction_code", code) \
            .execute()
        if not response.data:
            return code


# ─────────────────────────────────────────────
# 1. FULL REGISTRATION + RESERVATION (new customer)
# ─────────────────────────────────────────────
async def register_and_reserve(data: fullregistration):
    try:
        trip_resp = supabase.table("trip").select("*").eq("id", data.trip_id).execute()
        if not trip_resp.data:
            raise HTTPException(status_code=404, detail="Trip not found")

        trip = trip_resp.data[0]
        if trip["places"] <= 0:
            raise HTTPException(status_code=400, detail="No available places for this trip")

        customer_resp = supabase.table("customer").select("id").eq("email", data.email).execute()
        if customer_resp.data:
            customer_id = customer_resp.data[0]["id"]
        else:
            new_customer = Customer(
                fullname=data.fullname,
                phonnum=data.phonnum,
                email=data.email,
                birthdate=data.birthdate,
            )
            insert_resp = supabase.table("customer").insert({
                "fullname": new_customer.fullname,
                "phonnum": new_customer.phonnum,
                "email": new_customer.email,
                "birthdate": str(new_customer.birthdate),
            }).execute()
            customer_id = insert_resp.data[0]["id"]

        existing = supabase.table("reservation") \
            .select("*") \
            .eq("customer_id", customer_id) \
            .eq("trip_id", data.trip_id) \
            .execute()
        if existing.data:
            raise HTTPException(status_code=409, detail="Reservation already exists for this customer and trip")

        transaction_code = generate_unique_code(supabase)

        supabase.table("reservation").insert({
            "customer_id": customer_id,
            "trip_id": data.trip_id,
            "confirmation": False,
            "transaction_code": transaction_code,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }).execute()

        supabase.table("trip").update({"places": trip["places"] - 1}).eq("id", data.trip_id).execute()
        trip_name = supabase.table("trip").select("name").eq("id", data.trip_id).execute().data[0]["name"]

        # Email 1 — pending, transaction code shown for office reference
        email_pending(data, trip_name, transaction_code)

        return {
            "message": "Reservation created successfully",
            "transaction_code": transaction_code,
            "customer_id": customer_id,
            "trip_id": data.trip_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# 2. RESERVE ONLY (existing customer by email)
# ─────────────────────────────────────────────
async def reserve(data: Reservation):
    try:
        customer_resp = supabase.table("customer").select("id, fullname, email").eq("email", data.email).execute()
        if not customer_resp.data:
            raise HTTPException(status_code=404, detail="Customer not found")

        customer = customer_resp.data[0]
        customer_id = customer["id"]

        trip_resp = supabase.table("trip").select("*").eq("id", data.trip_id).execute()
        if not trip_resp.data:
            raise HTTPException(status_code=404, detail="Trip not found")

        trip = trip_resp.data[0]
        if trip["places"] <= 0:
            raise HTTPException(status_code=400, detail="No available places for this trip")

        existing = supabase.table("reservation") \
            .select("*") \
            .eq("customer_id", customer_id) \
            .eq("trip_id", data.trip_id) \
            .execute()
        if existing.data:
            raise HTTPException(status_code=409, detail="Reservation already exists")

        transaction_code = generate_unique_code(supabase)

        supabase.table("reservation").insert({
            "customer_id": customer_id,
            "trip_id": data.trip_id,
            "confirmation": False,
            "transaction_code": transaction_code,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }).execute()

        supabase.table("trip").update({"places": trip["places"] - 1}).eq("id", data.trip_id).execute()

        # Email 1 — pending, transaction code shown for office reference
        customer_data = SimpleNamespace(
            fullname = customer["fullname"],
            email    = customer["email"],
        )
        email_pending(customer_data, trip["name"], transaction_code)

        return {
            "message": "Reservation created successfully",
            "transaction_code": transaction_code,
            "customer_id": customer_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# 3. GET RESERVATION by transaction code
# ─────────────────────────────────────────────
async def get_reservation(transaction_code: str):
    try:
        resp = supabase.table("reservation") \
            .select("*, customer(*), trip(*)") \
            .eq("transaction_code", transaction_code) \
            .execute()
        if not resp.data:
            raise HTTPException(status_code=404, detail="Reservation not found")
        return resp.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# 4. CANCEL RESERVATION by transaction code
# ─────────────────────────────────────────────
async def cancel_reservation(transaction_code: str):
    try:
        resp = supabase.table("reservation") \
            .select("*, customer(*), trip(*)") \
            .eq("transaction_code", transaction_code) \
            .execute()
        if not resp.data:
            raise HTTPException(status_code=404, detail="Reservation not found")

        res        = resp.data[0]
        customer   = res.get("customer") or {}
        trip       = res.get("trip")     or {}

        supabase.table("reservation") \
            .delete() \
            .eq("transaction_code", transaction_code) \
            .execute()

        # Restore place count
        trip_resp = supabase.table("trip").select("places").eq("id", res["trip_id"]).execute()
        if trip_resp.data:
            current_places = trip_resp.data[0]["places"]
            supabase.table("trip").update({"places": current_places + 1}).eq("id", res["trip_id"]).execute()

        # Email 3 — cancelled
        if customer.get("email"):
            email_cancelled(
                fullname  = customer.get("fullname", "Customer"),
                email     = customer["email"],
                trip_name = trip.get("name", "your trip"),
            )

        return {"message": "Reservation cancelled successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# 5. CONFIRM BOOKING (admin only)
# ─────────────────────────────────────────────
async def confirm_booking(transaction_code: str):
    try:
        resp = supabase.table("reservation") \
            .select("*, customer(*), trip(*)") \
            .eq("transaction_code", transaction_code) \
            .execute()

        if not resp.data:
            raise HTTPException(status_code=404, detail="Reservation not found")

        reservation = resp.data[0]

        if reservation["confirmation"]:
            raise HTTPException(status_code=400, detail="Booking already confirmed")

        supabase.table("reservation") \
            .update({"confirmation": True}) \
            .eq("transaction_code", transaction_code) \
            .execute()

        customer = reservation["customer"]
        trip     = reservation["trip"]

        # Email 2 — confirmed, transaction code revealed
        customer_data = SimpleNamespace(
            fullname = customer["fullname"],
            email    = customer["email"],
        )
        email_confirmed(
            data             = customer_data,
            trip_name        = trip["name"],
            transaction_code = transaction_code,
        )

        return {
            "message": "Booking confirmed successfully",
            "transaction_code": transaction_code,
            "customer": customer["fullname"],
            "trip": trip["name"],
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
