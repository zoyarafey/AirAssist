from utils.csv_handler import read_csv, find_one, find_many, update_one, append_row
from utils.helpers import generate_pnr, generate_booking_id, now_str, calc_taxes, baggage_for_cabin, format_date
from tools.logger import audit_log
from typing import Optional, List

# ── Search Flights ────────────────────────────────────────────────────────────
def search_flights(origin: str, destination: str, depart_date: str, cabin: Optional[str] = None) -> dict:
    flights = read_csv("flights.csv")
    results = []
    for f in flights:
        match = (
            f["origin"].upper() == origin.upper() and
            f["destination"].upper() == destination.upper() and
            f["depart_date"] == depart_date and
            int(f.get("seats_available", 0)) > 0
        )
        if match:
            if cabin and f["cabin"].lower() != cabin.lower():
                continue
            results.append(f)
    if not results:
        return {"success": False,
                "message": f"No available flights found from **{origin.upper()}** to **{destination.upper()}** on **{depart_date}**.\n\nPlease try:\n- Different dates\n- Different cabin class\n- Nearby airports"}
    return {"success": True, "flights": results[:5]}  # show top 5

# ── Quote Fare ─────────────────────────────────────────────────────────────────
def quote_fare(flight_id: str, cabin: str) -> dict:
    flight = find_one("flights.csv", "flight_id", flight_id)
    if not flight:
        return {"success": False, "message": "Flight not found."}
    base = float(flight["base_fare"])
    taxes = calc_taxes(base)
    return {"success": True, "base_fare": base, "taxes": taxes, "total": base + taxes,
            "baggage": baggage_for_cabin(cabin), "cabin": cabin}

# ── Get User Bookings ──────────────────────────────────────────────────────────
def get_user_bookings(user_id: str) -> dict:
    bookings = find_many("bookings.csv", "user_id", user_id)
    if not bookings:
        return {"success": True, "bookings": [], "message": "You have no bookings yet."}
    # Enrich with user name
    user = find_one("users.csv", "user_id", user_id)
    for b in bookings:
        b["passenger_name"] = user.get("full_name", "") if user else ""
        b["passenger_email"] = user.get("email", "") if user else ""
        b["passenger_phone"] = user.get("phone", "") if user else ""
    return {"success": True, "bookings": bookings}

# ── Get Single Booking ─────────────────────────────────────────────────────────
def get_booking_details(pnr: str, user_id: str) -> dict:
    booking = find_one("bookings.csv", "pnr", pnr)
    if not booking:
        return {"success": False, "message": f"No booking found with PNR **{pnr}**."}
    # Security: user can only access their own bookings
    if booking["user_id"] != user_id:
        return {"success": False, "message": "Access denied. This booking does not belong to your account."}
    user = find_one("users.csv", "user_id", user_id)
    booking["passenger_name"] = user.get("full_name", "") if user else ""
    booking["passenger_email"] = user.get("email", "") if user else ""
    booking["passenger_phone"] = user.get("phone", "") if user else ""
    return {"success": True, "booking": booking}

# ── Create Booking ─────────────────────────────────────────────────────────────
def create_booking(user_id: str, flight_id: str, cabin: str, payment_method: str = "demo", extra_passengers: list = None, total_fare_override: float = None) -> dict:
    flight = find_one("flights.csv", "flight_id", flight_id)
    if not flight:
        return {"success": False, "message": "Flight not found. Please search again."}

    if int(flight.get("seats_available", 0)) < 1:
        return {"success": False, "message": "Sorry, no seats available on this flight."}

    # Validate cabin matches flight
    if flight["cabin"].lower() != cabin.lower():
        return {"success": False, "message": f"This flight only offers **{flight['cabin']}** class."}

    user = find_one("users.csv", "user_id", user_id)
    if not user:
        return {"success": False, "message": "User not found."}

    base_fare = float(flight["base_fare"])
    taxes = calc_taxes(base_fare)
    # PART 3: If total_fare_override provided (multi-passenger), use it; else single-passenger calc
    total_fare = round(total_fare_override, 2) if total_fare_override is not None else round(base_fare + taxes, 2)
    pnr = generate_pnr()
    booking_id = generate_booking_id()
    baggage = baggage_for_cabin(cabin)

    new_booking = {
        "booking_id": booking_id,
        "user_id": user_id,
        "pnr": pnr,
        "flight_id": flight_id,
        "flight_number": flight.get("flight_number", ""),
        "origin": flight["origin"],
        "destination": flight["destination"],
        "origin_city": flight.get("origin_city", ""),
        "destination_city": flight.get("destination_city", ""),
        "origin_airport": flight.get("origin_airport", ""),
        "destination_airport": flight.get("destination_airport", ""),
        "depart_date": flight["depart_date"],
        "depart_time": flight["depart_time"],
        "arrive_time": flight["arrive_time"],
        "cabin": cabin,
        "fare_class": flight["fare_class"],
        "status": "CONFIRMED",
        "base_fare": base_fare,
        "taxes": taxes,
        "total_fare": total_fare,
        "baggage_allowance": baggage,
        "created_at": now_str(),
    }

    append_row("bookings.csv", new_booking)

    # Reduce seat count
    flights_all = read_csv("flights.csv")
    for f in flights_all:
        if f["flight_id"] == flight_id:
            f["seats_available"] = str(int(f["seats_available"]) - 1)
    from utils.csv_handler import write_csv
    write_csv("flights.csv", flights_all)

    # Add passenger info for ticket display
    new_booking["passenger_name"] = user.get("full_name", "")
    new_booking["passenger_email"] = user.get("email", "")
    new_booking["passenger_phone"] = user.get("phone", "")
    # FEATURE 4: Store extra passenger names (all beyond the head passenger)
    new_booking["extra_passengers"] = extra_passengers or []

    audit_log(user_id, "CREATE_BOOKING", "booking", booking_id,
              {"flight_id": flight_id, "cabin": cabin},
              {"pnr": pnr, "total": total_fare}, "SUCCESS")

    return {"success": True, "booking": new_booking,
            "message": f"✅ Booking confirmed! Your PNR is **{pnr}**"}

# ── Cancel Booking ─────────────────────────────────────────────────────────────
def cancel_booking(pnr: str, user_id: str, reason: Optional[str] = None) -> dict:
    booking = find_one("bookings.csv", "pnr", pnr.upper().strip())
    if not booking:
        return {"success": False, "message": f"No booking found with PNR **{pnr}**. Please check and try again."}

    # Security check
    if booking["user_id"] != user_id:
        return {"success": False, "message": "Access denied. This booking does not belong to your account."}

    if booking["status"] == "CANCELLED":
        return {"success": False, "message": f"Booking **{pnr}** is already cancelled."}

    # Fetch cancellation policy
    fare_class = booking.get("fare_class", "Y")
    policies = read_csv("policies.csv")
    policy = next((p for p in policies if p["topic"] == "cancellation" and
                   (p["fare_class"] == fare_class or p["fare_class"] == "all")), None)
    refund_msg = policy["rule_summary"] if policy else "Refund as per policy"

    # Update status
    update_one("bookings.csv", "pnr", pnr.upper().strip(), {"status": "CANCELLED"})

    audit_log(user_id, "CANCEL_BOOKING", "booking", booking["booking_id"],
              {"pnr": pnr, "reason": reason or "user_requested"},
              {"status": "CANCELLED"}, "SUCCESS")

    return {
        "success": True,
        "pnr": pnr,
        "message": f"✅ Booking **{pnr}** has been successfully cancelled.\n\n📋 **Refund Policy:** {refund_msg}\n\n💰 Refund will be processed in 7–10 business days."
    }

# ── Update Booking Flight Details ──────────────────────────────────────────────
def update_booking_journey(pnr: str, user_id: str, field: str, new_value: str) -> dict:
    booking = find_one("bookings.csv", "pnr", pnr.upper().strip())
    if not booking:
        return {"success": False, "message": f"No booking found with PNR **{pnr}**."}
    if booking["user_id"] != user_id:
        return {"success": False, "message": "Access denied."}
    if booking["status"] == "CANCELLED":
        return {"success": False, "message": "Cannot update a cancelled booking."}

    old_value = booking.get(field, "")

    if field in ["origin", "destination", "depart_date"]:
        # Need to find a new matching flight
        new_origin = new_value.upper() if field == "origin" else booking["origin"]
        new_dest = new_value.upper() if field == "destination" else booking["destination"]
        new_date = new_value if field == "depart_date" else booking["depart_date"]
        cabin = booking["cabin"]

        result = search_flights(new_origin, new_dest, new_date, cabin)
        if not result["success"]:
            return {"success": False, "message": result["message"]}

        new_flight = result["flights"][0]
        updates = {
            "flight_id": new_flight["flight_id"],
            "flight_number": new_flight.get("flight_number", ""),
            "origin": new_flight["origin"],
            "destination": new_flight["destination"],
            "origin_city": new_flight.get("origin_city", ""),
            "destination_city": new_flight.get("destination_city", ""),
            "depart_date": new_flight["depart_date"],
            "depart_time": new_flight["depart_time"],
            "arrive_time": new_flight["arrive_time"],
        }
        update_one("bookings.csv", "pnr", pnr.upper().strip(), updates)

        # Return updated booking for ticket display
        updated = find_one("bookings.csv", "pnr", pnr.upper().strip())
        user = find_one("users.csv", "user_id", user_id)
        updated["passenger_name"] = user.get("full_name", "") if user else ""
        updated["passenger_email"] = user.get("email", "") if user else ""
        updated["passenger_phone"] = user.get("phone", "") if user else ""

        audit_log(user_id, "UPDATE_BOOKING", "booking", booking["booking_id"],
                  {"field": field, "old": old_value, "new": new_value},
                  {"new_flight": new_flight["flight_id"]}, "SUCCESS")

        return {"success": True, "booking": updated, "message": "✅ Journey updated! Here is your new boarding pass:"}

    return {"success": False, "message": f"Cannot update field '{field}' directly."}


def format_booking_for_display(booking: dict) -> dict:
    """
    Maps raw CSV booking fields to the shape BoardingPass component expects.
    Fixes the origin->source, destination->destination mismatch.
    Status is also normalized to lowercase for frontend comparisons.
    """
    from utils.helpers import format_date
    import hashlib
    pnr = booking.get("pnr", "")
    gate_num = (sum(ord(c) for c in pnr) % 20) + 1
    return {
        "booking_id": booking.get("booking_id", ""),
        "pnr": pnr,
        "flight_number": booking.get("flight_number", ""),
        # FIX: map origin->source and destination->destination for BoardingPass
        "source": booking.get("origin", ""),
        "destination": booking.get("destination", ""),
        "source_city": booking.get("origin_city", ""),
        "destination_city": booking.get("destination_city", ""),
        "source_airport": booking.get("origin_airport", ""),
        "destination_airport": booking.get("destination_airport", ""),
        "date": format_date(booking.get("depart_date", "")),
        "time": booking.get("depart_time", ""),
        "arrive_time": booking.get("arrive_time", ""),
        "cabin": booking.get("cabin", ""),
        "fare_class": booking.get("fare_class", ""),
        # FIX: normalize status to lowercase so BoardingPass === checks work
        "status": booking.get("status", "CONFIRMED").lower(),
        "base_fare": booking.get("base_fare", ""),
        "taxes": booking.get("taxes", ""),
        "total_fare": booking.get("total_fare", ""),
        "baggage_allowance": booking.get("baggage_allowance", "23kg"),
        "gate": f"A{gate_num}",
        "terminal": "Terminal 1",
        "airline": "AirAssist: Airline ",
        # Passenger info
        "passenger_name": booking.get("passenger_name", ""),
        "passenger_email": booking.get("passenger_email", ""),
        "passenger_phone": booking.get("passenger_phone", ""),
    }


def search_flights_no_date(origin: str, destination: str, cabin: str = None) -> dict:
    """
    Search flights by origin+destination. Cabin is now optional — if not provided,
    returns all cabin classes so user sees full list without being asked cabin first.
    """
    from datetime import datetime
    flights = read_csv("flights.csv")
    today = datetime.today().date()
    results = []

    for f in flights:
        if (f["origin"].upper() == origin.upper() and
                f["destination"].upper() == destination.upper() and
                int(f.get("seats_available", 0)) > 0):
            # Filter by cabin only if specified
            if cabin and f["cabin"].lower() != cabin.lower():
                continue
            try:
                fdate = datetime.strptime(f["depart_date"], "%Y-%m-%d").date()
                if fdate >= today:
                    results.append(f)
            except:
                results.append(f)

    if not results:
        return {
            "success": False,
            "message": (
                f"No available flights found from **{origin.upper()}** to **{destination.upper()}**.\n\n"
                f"Please try different airports.\n\n"
                f"Type **book a flight** to start again."
            )
        }

    results.sort(key=lambda x: (x.get("depart_date", ""), x.get("cabin", "")))
    return {"success": True, "flights": results[:8]}
