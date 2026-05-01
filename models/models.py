from pydantic import BaseModel, EmailStr
from datetime import date, time
from typing import Optional


class Admin(BaseModel):
    username: str
    password: str
    privileges: str


class Customer(BaseModel):
    fullname: str
    phonnum: str
    email: str
    birthdate: date


class Hotel(BaseModel):
    name: str
    rating: int
    img: str


class Flight(BaseModel):
    company: str
    flight_code: str
    class_: str = "Economy"  # 'class' is a reserved keyword in Python
    departure_location: str
    departure_time: str      # e.g. "10:45"
    arrival_location: str
    arrival_time: str        # e.g. "14:30"
    duration: str            # e.g. "2h 15m"
    is_direct: bool = True


class Trip(BaseModel):
    name: str
    description: str
    price: float
    places: int
    start_date: date
    end_date: date
    visual: bool
    media: list[str]
    adults: int
    children: int
    room: int
    country: str
    hotel: Hotel
    outbound_flight: Flight          # e.g. LHR -> NAP
    return_flight: Flight            # e.g. NAP -> LHR


class Reservation(BaseModel):
    email: str
    trip_id: int
    confirmation: bool = False


class fullregistration(BaseModel):
    fullname: str
    phonnum: str
    email: str
    birthdate: date
    trip_id: int
    confirmation: bool = False

class VerifyRequest(BaseModel):
    token: str
    answer: str
