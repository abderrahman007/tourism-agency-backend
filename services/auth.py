import bcrypt
import jwt
from datetime import datetime, timedelta, timezone  # ✅ added timedelta
from dotenv import load_dotenv
import os
from db.supabase import supabase
from fastapi import Depends, HTTPException,status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
TOKEN_EXPIRY_HOURS = 24


def create_token(username: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": username,
        "iat": now,
        "exp": now + timedelta(hours=TOKEN_EXPIRY_HOURS)  # ✅ fixed
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def authenticate_user(username: str, password: str) -> dict | None:
    response = supabase.table("admin").select("password").eq("username", username).execute()

    if not response.data:
        return None

    stored_password = response.data[0]["password"]

    if not bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
        return None

    token = create_token(username)
    return {
        "access_token": token,
        "token_type": "bearer",
        "username": username
    }


def verify_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    return payload  