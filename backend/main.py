from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from auth import login_user, signup_user
from orchestrator import process_message
from tools.booking_tools import get_user_bookings, format_booking_for_display
from tools.customer_tools import get_user_profile

app = FastAPI(title="AirAssist API", version="2.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    email: str
    password: str

class SignupRequest(BaseModel):
    name: str
    email: str
    phone: str
    password: str
    address: Optional[str] = ""

class ChatRequest(BaseModel):
    customer_id: str
    message: str
    customer_info: dict

@app.get("/")
def root():
    return {"message": "AirAssist API v2.1 is running", "status": "ok"}

@app.post("/login")
def login(req: LoginRequest):
    result = login_user(req.email, req.password)
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result.get("message"))
    return result

@app.post("/signup")
def signup(req: SignupRequest):
    result = signup_user(req.name, req.email, req.phone, req.password, req.address)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result

@app.post("/chat")
def chat(req: ChatRequest):
    if not req.customer_id or not req.message.strip():
        raise HTTPException(status_code=400, detail="customer_id and message are required")
    return process_message(req.customer_id, req.message, req.customer_info)

@app.get("/bookings/{customer_id}")
def get_bookings(customer_id: str):
    # FIX 2a: pass raw bookings through formatter so frontend gets correct field names
    result = get_user_bookings(customer_id)
    if result.get("bookings"):
        result["bookings"] = [format_booking_for_display(b) for b in result["bookings"]]
    return result

@app.get("/customer/{customer_id}")
def get_customer(customer_id: str):
    # FIX 2b: used by frontend to refresh user data after profile update
    result = get_user_profile(customer_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail="Customer not found")
    u = result["user"]
    return {
        "success": True,
        "customer_id": u["user_id"],
        "user_id": u["user_id"],
        "name": u.get("full_name", ""),
        "full_name": u.get("full_name", ""),
        "email": u.get("email", ""),
        "phone": u.get("phone", ""),
        "address": u.get("address", ""),
        "username": u.get("username", ""),
    }
