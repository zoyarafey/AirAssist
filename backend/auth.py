from utils.csv_handler import read_csv, append_row, find_one
from utils.helpers import generate_user_id, now_str

def login_user(email: str, password: str) -> dict:
    users = read_csv("users.csv")
    for u in users:
        if (u.get("email","").strip().lower() == email.strip().lower() and
                u.get("password_hash","").strip() == password.strip()):
            return {
                "success": True,
                "customer_id": u["user_id"],
                "user_id": u["user_id"],
                "name": u.get("full_name", u.get("username","")),
                "full_name": u.get("full_name",""),
                "username": u.get("username",""),
                "email": u["email"],
                "phone": u.get("phone",""),
                "address": u.get("address","")
            }
    return {"success": False, "message": "Invalid email or password. Please try again."}

def signup_user(name, email, phone, password, address):
    # Read once only
    users = read_csv("users.csv")
    
    # Use next() with a generator — stops at first match, doesn't loop all rows
    existing = next((u for u in users if u["email"].lower() == email.lower()), None)
    if existing:
        return {"success": False, "message": "An account with this email already exists."}
    
    # Generate user_id from length — no second read needed
    new_id = f"USR{str(len(users) + 1).zfill(6)}"
    
    new_user = {
        "user_id":       new_id,
        "username":      email.split("@")[0],
        "password_hash": password,
        "full_name":     name,
        "email":         email.lower().strip(),
        "phone":         phone.strip(),
        "address":       address.strip(),
    }
    append_row("users.csv", new_user)
    return {"success": True, "user": new_user}