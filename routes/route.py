from fastapi import APIRouter, Depends, HTTPException, Response
from services.search import search_trips
from services.trip import visualize_trips, get_trip_details,get_local_trips, add_trip, calculate_cost, get_overview,get_last_trip
from services.booking import register_and_reserve, cancel_reservation, reserve, confirm_booking, get_reservation
from models.models import fullregistration, Reservation, Trip,VerifyRequest
from services.auth import authenticate_user, get_current_user
from services.captcha import create_captcha, verify_captcha


router = APIRouter()


@router.get("/visual")
async def get_v():
    return await visualize_trips()

@router.get("/last_trips")
async def grt_last():
    return await get_last_trip()



@router.get("/search_trips")
async def search_t(startdate: str, enddate: str, location: str, numadults: int, numchild: int, rooms: int):
    return await search_trips(startdate, enddate, location, numadults, numchild, rooms)

    
@router.get("/local_trips")
async def get_local_trips_endpoint():
    return await get_local_trips()


@router.post("/register_and_reserve")
async def register_and_reserve_endpoint(data: fullregistration):
    return await register_and_reserve(data)


@router.delete("/cancel_reservation/{transaction_code}")
async def cancel_reservation_endpoint(transaction_code: str):
    return await cancel_reservation(transaction_code)


@router.post("/reserve")
async def reserve_endpoint(data: Reservation):
    return await reserve(data)


@router.get("/trip/{trip_id}")
async def get_trip_details_endpoint(trip_id: int, current_user: dict = Depends(get_current_user)):
    return {
        "Trip": await get_trip_details(trip_id),
        "User": current_user["sub"]
    }


@router.post("/admin/trip")
async def add_trip_endpoint(data: Trip, current_user: dict = Depends(get_current_user)):
    return {
        "res": await add_trip(data),
        "User": current_user["sub"]
    }


@router.post("/admin/authenticate")
async def authenticate_user_endpoint(username: str, password: str):
    return authenticate_user(username, password)


@router.get("/admin/reservation/{transaction_code}")
async def get_reservation_endpoint(transaction_code: str, current_user: dict = Depends(get_current_user)):
    return {
        "res": await get_reservation(transaction_code),
        "User": current_user["sub"]
    }


@router.patch("/admin/confirm/{transaction_code}")
async def confirm_booking_endpoint(transaction_code: str, current_user: dict = Depends(get_current_user)):
    return {
        "res": await confirm_booking(transaction_code),
        "User": current_user["sub"]
    }


@router.get("/admin/cost/{trip_id}")
async def calculate_cost_endpoint(trip_id: int, current_user: dict = Depends(get_current_user)):
    return {
        "res": await calculate_cost(trip_id),
        "User": current_user["sub"]
    }


@router.get("/admin/overview")
async def get_overview_endpoint(current_user: dict = Depends(get_current_user)):
    return {
        "res": await get_overview(),
        "User": current_user["sub"]
    }


@router.get("/captcha")
def get_captcha():
    token, image_bytes = create_captcha()
    return Response(
        content=image_bytes,
        media_type="image/png",
        headers={"X-Captcha-Token": token,
                 "Access-Control-Expose-Headers": "X-Captcha-Token"}
    )

@router.post("/verify")
def verify(body: VerifyRequest):
    if not verify_captcha(body.token, body.answer):
        raise HTTPException(status_code=400, detail="Invalid or expired captcha")
    return {"ok": True, "message": "Verified!"}
