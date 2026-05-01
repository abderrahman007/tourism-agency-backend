import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

key = os.getenv("API_KEY")
url = os.getenv("BASE_URL")

if not key or not url:
    raise RuntimeError("API_KEY or BASE_URL not set in .env")
 
supabase = create_client(url, key)