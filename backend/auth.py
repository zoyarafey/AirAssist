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

def signup_user(name: str, email: str, phone: str, password: str, address: str = "") -> dict:
    existing = find_one("users.csv", "email", email)
    if existing:
        return {"success": False, "message": "An account with this email already exists. Please log in."}
    uid = generate_user_id()
    username = email.split("@")[0].replace(".", "_")
    new_user = {
        "user_id": uid,
        "username": username,
        "password_hash": password,
        "full_name": name,
        "email": email,
        "phone": phone,
        "address": address
    }
    append_row("users.csv", new_user)
    return {
        "success": True,
        "customer_id": uid,
        "user_id": uid,
        "name": name,
        "full_name": name,
        "username": username,
        "email": email,
        "phone": phone,
        "address": address
    }
