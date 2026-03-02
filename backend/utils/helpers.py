import random
import string
from datetime import datetime

def generate_pnr() -> str:
    chars = string.ascii_uppercase + string.digits
    code = ''.join(random.choices(chars, k=5))
    return f"JHAN-{code}"

def generate_user_id() -> str:
    # FIX 1: Use timestamp + random suffix instead of row count
    # Row count caused duplicate IDs when called multiple times in same second
    ts = datetime.now().strftime("%f")  # microseconds = unique per call
    suffix = ''.join(random.choices(string.digits, k=3))
    return f"USR{ts[:4]}{suffix}"

def generate_booking_id() -> str:
    # FIX 1 (same): Use timestamp + random to avoid duplicates
    ts = datetime.now().strftime("%f")
    suffix = ''.join(random.choices(string.digits, k=4))
    return f"BK{ts}{suffix}"

def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def format_date(date_str: str) -> str:
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%b %d, %Y").upper()
    except:
        return date_str

def calc_taxes(base_fare: float) -> float:
    return round(base_fare * 0.18, 2)

def baggage_for_cabin(cabin: str) -> str:
    mapping = {
        "economy": "23kg", "premium economy": "28kg",
        "business": "32kg", "first": "40kg"
    }
    return mapping.get(cabin.lower(), "23kg")
