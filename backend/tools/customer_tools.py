from utils.csv_handler import find_one, update_one, read_csv
from tools.logger import audit_log

ALLOWED_FIELDS = {
    "email": "email",
    "phone": "phone",
    "address": "address",
    "full_name": "full_name",
    "name": "full_name",
    "username": "username",
}

def get_user_profile(user_id: str) -> dict:
    user = find_one("users.csv", "user_id", user_id)
    if not user:
        return {"success": False, "message": "User not found."}
    safe = {k: v for k, v in user.items() if k != "password_hash"}
    return {"success": True, "user": safe}

def update_user_field(user_id: str, field: str, new_value: str) -> dict:
    # Resolve alias (e.g. "name" -> "full_name")
    actual_field = ALLOWED_FIELDS.get(field.lower().strip())
    if not actual_field:
        return {"success": False, "message": f"'{field}' cannot be updated. You can update: name, email, phone, or address."}

    user = find_one("users.csv", "user_id", user_id)
    if not user:
        return {"success": False, "message": "User not found."}

    old_value = user.get(actual_field, "")
    success = update_one("users.csv", "user_id", user_id, {actual_field: new_value})

    if success:
        audit_log(user_id, "UPDATE_PROFILE", "user", user_id,
                  {"field": actual_field, "old": old_value, "new": new_value},
                  {"updated": True}, "SUCCESS")
        return {"success": True, "field": actual_field, "new_value": new_value,
                "message": f"Your {actual_field.replace('_',' ')} has been updated to **{new_value}**."}

    return {"success": False, "message": "Update failed. Please try again."}
