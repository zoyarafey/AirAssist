import re
from datetime import datetime

# SHARED EMAIL VALIDATION
# Bug: old validate_email accepted any domain (e.g. z@example.com, test@fake.com)
# because the regex only checked structure, not the domain name.
# Fix: allow only gmail.com, yahoo.com, outlook.com — checked explicitly.
# This function is imported by orchestrator.py via validate_field()
# so ALL chatbot profile updates automatically use this same rule.
ALLOWED_EMAIL_DOMAINS = {'gmail.com', 'yahoo.com', 'outlook.com'}

def validate_email(v: str) -> dict:
    v = v.strip().lower()
    # Must match: something@domain.tld with no spaces
    match = re.match(r'^[^\s@]+@([^\s@]+)$', v)
    if match:
        domain = match.group(1)
        if domain in ALLOWED_EMAIL_DOMAINS:
            return {"valid": True}
    return {
        "valid": False,
        "message": "Please enter a valid email address (example: name@gmail.com)"
    }

# SHARED PHONE VALIDATION
# Bug: old validate_phone stripped the + sign before checking, so:
#   - "9876543210" (no +) passed because stripped version had 10 digits
#   - "+12" passed in some cases
#   - no enforcement that + is required at the start
# Fix: enforce that number starts with +, then only digits, total digits 6-15
def validate_phone(v: str) -> dict:
    v = v.strip()
    # Must start with +
    if not v.startswith('+'):
        return {
            "valid": False,
            "message": "Please enter a valid phone number with country code (example: +919876543210)"
        }
    # After the +, only digits allowed (no spaces, dashes, letters)
    digits_only = v[1:]
    if not digits_only.isdigit():
        return {
            "valid": False,
            "message": "Please enter a valid phone number with country code (example: +919876543210)"
        }
    # Total digits (excluding +) must be between 6 and 15
    if not (6 <= len(digits_only) <= 15):
        return {
            "valid": False,
            "message": "Please enter a valid phone number with country code (example: +919876543210)"
        }
    return {"valid": True}

# These functions below are unchanged
def validate_date(v: str) -> dict:
    try:
        d = datetime.strptime(v, "%Y-%m-%d")
        if d.date() < datetime.today().date():
            return {"valid": False, "message": "Date cannot be in the past. Please enter a future date (YYYY-MM-DD)."}
        return {"valid": True}
    except:
        return {"valid": False, "message": "Please enter date in YYYY-MM-DD format (e.g. 2026-03-15)."}

def validate_name(v: str) -> dict:
    if len(v.strip()) >= 2:
        return {"valid": True}
    return {"valid": False, "message": "Name must be at least 2 characters."}

def validate_field(field: str, value: str) -> dict:
    validators = {
        "email": validate_email,
        "phone": validate_phone,
        "date": validate_date,
        "depart_date": validate_date,
        "full_name": validate_name,
        "name": validate_name,
    }
    fn = validators.get(field)
    if fn:
        return fn(value)
    return {"valid": True}
