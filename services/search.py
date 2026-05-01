from fastapi import HTTPException
from db.supabase import supabase
from datetime import datetime


# ─────────────────────────────────────────────
# SEARCH TRIPS
# ─────────────────────────────────────────────

async def search_trips(startdate, enddate, location, numadults, numchild, rooms):
    try:
        query = (
            supabase
            .table("trip")
            .select("*, hotel(*),outbound_flight(*),return_flight(*)")
            .eq("adults", numadults)
            .eq("children", numchild)
            .eq("room", rooms)
            .or_(f"name.ilike.%{location}%,country.ilike.%{location}%")
        )

        use_date_filter = startdate not in (None, "null") and enddate not in (None, "null")
        if use_date_filter:
            query = query.filter("date", "cs", f"[{startdate},{enddate})")
        
        today = datetime.now().date()
        query = query.gt("expired", today)

        return query.execute().data

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))