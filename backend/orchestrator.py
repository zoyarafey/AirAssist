from typing import Dict, Optional
from tools.booking_tools import (search_flights, search_flights_no_date, get_user_bookings,
                                  get_booking_details, create_booking, cancel_booking,
                                  update_booking_journey)
from tools.policy_tools import lookup_policy, detect_policy_topic
from tools.customer_tools import get_user_profile, update_user_field
from tools.validation import validate_field
from utils.helpers import format_date
from utils.airport_lookup import resolve_airport, format_airport_options

# ── Session store (in-memory per user) ────────────────────────────────────────
sessions: Dict[str, dict] = {}

def get_session(uid: str) -> dict:
    if uid not in sessions:
        sessions[uid] = {"state": None, "data": {}}
    return sessions[uid]

def set_session(uid: str, state: Optional[str], data: dict = {}):
    sessions[uid] = {"state": state, "data": data}

def clear_session(uid: str):
    sessions[uid] = {"state": None, "data": {}}

# ── Intent detection — broad keyword matching ──────────────────────────────────
INTENTS = {
    "show_bookings": [
        "my booking", "my flight", "my ticket", "show booking", "view booking",
        "check booking", "booking status", "my reservation", "show my", "see my booking",
        "list booking", "all booking", "what are my", "my trips"
    ],
    "create_booking": [
        "book a flight", "book flight", "new booking", "reserve a flight",
        "i want to fly", "book ticket", "purchase ticket", "buy ticket",
        "i want to book", "make a booking", "flight booking", "book a ticket",
        "i need a flight", "plan a flight"
    ],
    "cancel_booking": [
        "cancel", "cancellation", "cancel my flight", "cancel booking",
        "cancel ticket", "cancel my booking", "i want to cancel", "cancel reservation"
    ],
    "update_journey": [
        "update my flight", "change my flight", "update journey", "change destination",
        "change source", "change date", "modify flight", "update booking",
        "change my booking", "edit flight", "reschedule", "change my trip",
        "update my trip", "modify booking", "change origin", "change travel date"
    ],
    "update_profile": [
        "update my name", "change my name", "update email", "change email",
        "update phone", "change phone", "update contact", "update my address",
        "change address", "edit profile", "update profile", "change my details",
        "update my details", "edit my details", "change my email",
        "change my phone", "update my email", "update my phone",
        "change number", "update number", "my details", "edit contact"
    ],
    "greeting": [
        "hello", "hi", "hey", "good morning", "good evening",
        "good afternoon", "greetings", "howdy", "hii", "helo", "hiya"
    ],
    "help": [
        "help", "what can you do", "how to", "assist", "support",
        "options", "menu", "what can i do", "guide", "commands"
    ],
    "thanks": ["thank", "thanks", "thank you", "thx", "ty", "appreciated"],
    "bye": ["bye", "goodbye", "see you", "later", "take care"],
    "policy": [
        "policy", "policies", "rules", "allowance", "baggage", "luggage",
        "cancel policy", "refund", "check-in", "change fee", "no show",
        "what is the", "tell me about", "bag allowance", "carry on",
        "checked bag", "how much baggage", "baggage limit", "can i cancel",
        "how to cancel", "refund policy", "cancellation policy"
    ]
}

def detect_intent(msg: str) -> str:
    msg_lower = msg.lower().strip()
    for intent, keywords in INTENTS.items():
        for kw in keywords:
            if kw in msg_lower:
                return intent
    return "unknown"

# ── Response helpers ───────────────────────────────────────────────────────────
def text(msg: str) -> dict:
    return {"type": "text", "message": msg}

def ticket_response(booking: dict, msg: str = "") -> dict:
    return {
        "type": "ticket",
        "message": msg,
        "passenger_name": booking.get("passenger_name", ""),
        "passenger_email": booking.get("passenger_email", ""),
        "passenger_phone": booking.get("passenger_phone", ""),
        # FEATURE 4: extra_passengers list carries additional passenger names for display
        "extra_passengers": booking.get("extra_passengers", []),
        "pnr": booking.get("pnr", ""),
        "flight_number": booking.get("flight_number", ""),
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
        "status": booking.get("status", "CONFIRMED"),
        "total_fare": booking.get("total_fare", ""),
        "baggage_allowance": booking.get("baggage_allowance", ""),
        "gate": booking.get("gate", "A" + str(hash(booking.get("pnr",""))%20+1)),
        "terminal": booking.get("terminal", "Terminal 1"),
        "airline": "Jahan Chatbot Airlines"
    }

def flight_list_response(flights: list, msg: str) -> dict:
    return {"type": "flight_list", "flights": flights, "message": msg}

def _format_flight_list(flights: list, origin: str, dest: str) -> str:
    """PART 1: Format flight list with ALL required fields per flight."""
    lines = [f"✈️ Found **{len(flights)} available flight(s)** from **{origin}** to **{dest}**:\n"]
    for i, f in enumerate(flights, 1):
        seats = f.get("seats_available", "?")
        lines.append(
            f"**{i}.** {f['flight_number']} | {f['origin']}→{f['destination']} | "
            f"📅 {f['depart_date']} | 🕐 {f['depart_time']}→{f['arrive_time']} | "
            f"💺 {f['cabin']} | {seats} seats | ₹{float(f['base_fare']):,.0f}/person"
        )
    lines.append("\nType the **number** to select (e.g. 1, 2, 3)")
    return "\n".join(lines)

# ── Main processor ─────────────────────────────────────────────────────────────
def process_message(user_id: str, message: str, user_info: dict) -> dict:
    session = get_session(user_id)
    state = session["state"]
    data = session["data"]
    msg = message.strip()
    name = user_info.get("full_name") or user_info.get("name", "Passenger")
    first = name.split()[0]

    # ── MULTI-STEP STATE MACHINE ────────────────────────────────────────────

    # BOOKING FLOW
    if state == "booking_origin":
        if data.get("awaiting_origin_choice") and msg.strip().isdigit():
            idx = int(msg.strip()) - 1
            options = data.get("origin_options", [])
            if 0 <= idx < len(options):
                code = options[idx]["airport_code"]
                set_session(user_id, "booking_destination", {**data, "origin": code, "awaiting_origin_choice": False})
                return text(f"Origin set to **{code} — {options[idx]['airport_name']}** ✅\n\nNow enter your **destination**:\n*(city name, airport code, or airport name)*")
            return text(f"Please enter a number between 1 and {len(options)}.")
        result = resolve_airport(msg)
        if not result["found"]:
            return text(f"Could not find airport for \"{msg}\".\n\nTry:\n- City name: Delhi, Mumbai, London\n- Airport code: DEL, BOM, LHR\n- Airport name: Indira Gandhi International Airport")
        if result["multiple"]:
            options = result["airports"][:5]
            set_session(user_id, "booking_origin", {**data, "awaiting_origin_choice": True, "origin_options": options})
            return text(f"Multiple airports found for \"{msg}\". Please choose one:\n\n{format_airport_options(options)}\n\nType the number (1, 2, 3...)")
        code = result["code"]
        set_session(user_id, "booking_destination", {**data, "origin": code})
        return text(f"Origin set to **{code} — {result['airports'][0]['airport_name']}** ✅\n\nNow enter your **destination**:\n*(city name, airport code, or airport name)*")

    if state == "booking_destination":
        if data.get("awaiting_dest_choice") and msg.strip().isdigit():
            idx = int(msg.strip()) - 1
            options = data.get("dest_options", [])
            if 0 <= idx < len(options):
                code = options[idx]["airport_code"]
                set_session(user_id, "booking_passenger_count", {**data, "destination": code, "awaiting_dest_choice": False})
                return text(f"Destination set to **{code} — {options[idx]['airport_name']}** ✅\n\nHow many passengers are travelling? (1–6)")
            return text(f"Please enter a number between 1 and {len(options)}.")
        result = resolve_airport(msg)
        if not result["found"]:
            return text(f"Could not find airport for \"{msg}\".\n\nTry:\n- City name: Delhi, Mumbai, London\n- Airport code: DEL, BOM, LHR\n- Airport name: Heathrow Airport")
        if result["multiple"]:
            options = result["airports"][:5]
            set_session(user_id, "booking_destination", {**data, "awaiting_dest_choice": True, "dest_options": options})
            return text(f"Multiple airports found for \"{msg}\". Please choose one:\n\n{format_airport_options(options)}\n\nType the number (1, 2, 3...)")
        code = result["code"]
        # FEATURE 3: After destination, ask number of passengers (not cabin)
        set_session(user_id, "booking_passenger_count", {**data, "destination": code})
        return text(f"Destination set to **{code} — {result['airports'][0]['airport_name']}** ✅\n\nHow many passengers are travelling? (1–6)")


    # FEATURE 3: New state — ask how many passengers after destination confirmed
    if state == "booking_passenger_count":
        try:
            count = int(msg.strip())
            if count < 1 or count > 6:
                return text("Please enter a number between 1 and 6.")
        except ValueError:
            return text("Please enter a number between 1 and 6.")

        if count == 1:
            # Only head passenger — skip name collection, go straight to flight list
            result = search_flights_no_date(data["origin"], data["destination"])
            if not result["success"]:
                clear_session(user_id)
                return text(result["message"])
            flights = result["flights"]
            set_session(user_id, "booking_select_flight", {**data, "passenger_count": 1, "extra_passengers": [], "flights": flights})
            return text(_format_flight_list(flights, data["origin"], data["destination"]))
        else:
            # More than 1 — ask for names of additional passengers (head passenger auto-added)
            others = count - 1
            set_session(user_id, "booking_passenger_names", {**data, "passenger_count": count})
            return text(
                f"{count} passengers noted ✅\n\n"
                f"Please enter the names of the **other {others} passenger(s)**\n"
                f"*(Your own name is already included as Head Passenger)*\n\n"
                f"Type all names separated by commas:\n"
                f"e.g. `Rahul Sharma, Priya Mehta`"
            )

    # FEATURE 3: New state — collect extra passenger names
    if state == "booking_passenger_names":
        count = data.get("passenger_count", 2)
        expected_others = count - 1
        raw_names = [n.strip() for n in msg.split(",") if n.strip()]
        if len(raw_names) != expected_others:
            return text(
                f"Please enter exactly **{expected_others}** name(s) separated by commas.\n"
                f"e.g. `Rahul Sharma, Priya Mehta`"
            )
        for n in raw_names:
            if len(n) < 2:
                return text(f"Name '{n}' is too short. Each name must be at least 2 characters.")
        # PART 1: Immediately search flights after names — no cabin question
        result = search_flights_no_date(data["origin"], data["destination"])
        if not result["success"]:
            clear_session(user_id)
            return text(result["message"])
        flights = result["flights"]
        set_session(user_id, "booking_select_flight", {**data, "extra_passengers": raw_names, "flights": flights})
        return text(_format_flight_list(flights, data["origin"], data["destination"]))

    # booking_date state kept for backward compat but flow no longer reaches it
    if state == "booking_date":
        v = validate_field("date", msg)
        if not v["valid"]:
            return text(v["message"])
        set_session(user_id, "booking_cabin", {**data, "depart_date": msg})
        return text(f"Date noted ✅\n\nSelect **cabin class**:\n1️⃣ Economy\n2️⃣ Premium Economy\n3️⃣ Business\n4️⃣ First\n\nType the class name or number.")
    if state == "booking_cabin":
        cabin_map = {"1": "Economy", "2": "Premium Economy", "3": "Business", "4": "First",
                     "economy": "Economy", "premium economy": "Premium Economy",
                     "premium": "Premium Economy", "business": "Business", "first": "First"}
        cabin = cabin_map.get(msg.lower().strip())
        if not cabin:
            return text("Please enter a valid cabin class:\n1️⃣ Economy  2️⃣ Premium Economy  3️⃣ Business  4️⃣ First")
        # FIX 5: Search flights WITHOUT requiring date first
        # Shows all upcoming flights with dates so user picks the one they want
        result = search_flights_no_date(data["origin"], data["destination"], cabin)
        if not result["success"]:
            clear_session(user_id)
            return text(result["message"])
        flights = result["flights"]
        set_session(user_id, "booking_select_flight", {**data, "cabin": cabin, "flights": flights})
        # Show flights with date, seats, flight number
        lines = [f"✈️ Found **{len(flights)} available flight(s)** from **{data['origin']}** to **{data['destination']}** ({cabin}):\n"]
        for i, f in enumerate(flights, 1):
            seats = f.get("seats_available", "?")
            lines.append(f"**{i}.** {f['flight_number']} | 📅 {f['depart_date']} | 🕐 {f['depart_time']}→{f['arrive_time']} | 💺 {seats} seats | ₹{float(f['base_fare']):,.0f}")
        lines.append("\nType the **number** to select (e.g. 1, 2, 3)")
        return text("\n".join(lines))

    if state == "booking_select_flight":
        try:
            idx = int(msg.strip()) - 1
            flights = data.get("flights", [])
            if idx < 0 or idx >= len(flights):
                return text(f"Please enter a number between 1 and {len(flights)}.")
            chosen = flights[idx]
            pax_count = data.get("passenger_count", 1)
            base_per = float(chosen["base_fare"])
            # PART 2: Total = (base per person × passengers) + 18% tax on combined
            subtotal = round(base_per * pax_count, 2)
            taxes = round(subtotal * 0.18, 2)
            total = round(subtotal + taxes, 2)
            cabin = chosen.get("cabin", "Economy")
            baggage = chosen.get("baggage_allowance", "23kg") if "baggage_allowance" in chosen else "23kg"
            set_session(user_id, "booking_payment", {
                **data, "flight_id": chosen["flight_id"], "chosen_flight": chosen,
                "cabin": cabin, "total_fare_all": total
            })
            # PART 2: Exact summary format as required
            pax_line = f"₹{base_per:,.0f} × {pax_count} passenger{'s' if pax_count > 1 else ''} = ₹{subtotal:,.0f}"
            return text(
                f"Flight Selected: {chosen['flight_number']}\n"
                f"Route: {chosen['origin']} → {chosen['destination']}\n"
                f"Date: {chosen['depart_date']}\n"
                f"Cabin: {cabin}\n\n"
                f"💰 Fare Breakdown:\n"
                f"Base Fare: {pax_line}\n"
                f"Taxes (18%): ₹{taxes:,.0f}\n"
                f"Total: ₹{total:,.0f}\n"
                f"Baggage: {baggage}\n\n"
                f"Please confirm this flight (Yes / No)"
            )
        except ValueError:
            return text("Please enter a valid number to select a flight.")

    if state == "booking_payment":
        if msg.lower() in ["confirm", "yes", "y", "ok", "book", "proceed"]:
            extra = data.get("extra_passengers", [])
            cabin = data.get("cabin", "Economy")
            total_fare_all = data.get("total_fare_all")  # PART 3: combined fare for all passengers
            result = create_booking(user_id, data["flight_id"], cabin,
                                    extra_passengers=extra, total_fare_override=total_fare_all)
            clear_session(user_id)
            if result["success"]:
                return {**ticket_response(result["booking"], "🎉 Booking confirmed! Here is your boarding pass:"),}
            return text(f"❌ {result['message']}")
        elif msg.lower() in ["cancel", "no", "n", "back"]:
            clear_session(user_id)
            return text("Booking cancelled. Type **book a flight** to start again.")
        else:
            return text("Please type **Yes** to confirm the booking or **No** to cancel.")

    # CANCEL FLOW
    if state == "cancel_pnr":
        result = cancel_booking(msg.upper().strip(), user_id)
        clear_session(user_id)
        return text(result["message"])

    # UPDATE JOURNEY FLOW
    if state == "update_journey_pnr":
        result = get_booking_details(msg.upper().strip(), user_id)
        if not result["success"]:
            clear_session(user_id)
            return text(result["message"])
        set_session(user_id, "update_journey_field", {**data, "pnr": msg.upper().strip()})
        return text(
            f"Found booking **{msg.upper()}** ✅\n\n"
            f"What would you like to change?\n"
            f"- **origin** — change departure airport\n"
            f"- **destination** — change arrival airport\n"
            f"- **date** — change travel date\n\n"
            f"Type one of the options above."
        )

    if state == "update_journey_field":
        field_map = {
            "origin": "origin", "source": "origin", "departure": "origin", "from": "origin",
            "destination": "destination", "dest": "destination", "to": "destination", "arrival": "destination",
            "date": "depart_date", "travel date": "depart_date", "depart date": "depart_date"
        }
        field = field_map.get(msg.lower().strip())
        if not field:
            return text("Please type **origin**, **destination**, or **date** to select what to change.")
        set_session(user_id, "update_journey_value", {**data, "field": field})
        prompts = {
            "origin": "new departure airport code (e.g. BOM, BLR)",
            "destination": "new destination airport code (e.g. SIN, DXB)",
            "depart_date": "new travel date in YYYY-MM-DD format (e.g. 2026-04-10)"
        }
        return text(f"Please enter the **{prompts[field]}**:")

    if state == "update_journey_value":
        field = data["field"]
        v = validate_field(field, msg)
        if not v["valid"]:
            return text(v["message"])
        new_val = msg.upper().strip() if field != "depart_date" else msg.strip()
        result = update_booking_journey(data["pnr"], user_id, field, new_val)
        clear_session(user_id)
        if result["success"] and "booking" in result:
            return {**ticket_response(result["booking"], result["message"])}
        return text(result["message"])

    # UPDATE PROFILE FLOW
    if state == "update_profile_field":
        field_map = {
            "name": "full_name", "full name": "full_name", "my name": "full_name",
            "email": "email", "mail": "email", "my email": "email",
            "phone": "phone", "number": "phone", "contact": "phone",
            "mobile": "phone", "my phone": "phone", "my number": "phone",
            "address": "address", "my address": "address", "location": "address"
        }
        field = field_map.get(msg.lower().strip())
        if not field:
            return text("Please choose what to update:\n- **name**\n- **email**\n- **phone**\n- **address**")
        set_session(user_id, "update_profile_value", {**data, "field": field})
        labels = {"full_name": "full name", "email": "email address", "phone": "phone number", "address": "address"}
        return text(f"Please enter your **new {labels.get(field, field)}**:")

    if state == "update_profile_value":
        field = data["field"]
        v = validate_field(field, msg)
        if not v["valid"]:
            return text(v["message"])
        result = update_user_field(user_id, field, msg.strip())
        clear_session(user_id)
        return text(f"{'✅' if result['success'] else '❌'} {result['message']}")

    # ── FRESH INTENT ROUTING ────────────────────────────────────────────────
    intent = detect_intent(msg)

    if intent == "greeting":
        return text(
            f"Hello **{first}**! 👋 Welcome to **Jahan Chatbot Airlines** support.\n\n"
            f"Here's what I can help you with:\n"
            f"🎫 **Book a flight** — search and book flights\n"
            f"📋 **My bookings** — view your boarding passes\n"
            f"❌ **Cancel booking** — cancel a flight\n"
            f"✏️ **Update my flight** — change date, origin, destination\n"
            f"👤 **Update my email/phone/name** — edit your profile\n"
            f"🧳 **Baggage policy** — check bag rules\n"
            f"📜 **Cancellation policy** — refund rules\n\n"
            f"How can I assist you today?"
        )

    if intent == "help":
        return text(
            "Here's everything I can do:\n\n"
            "✈️ **Flights**\n"
            "→ \"book a flight\" — start a new booking\n"
            "→ \"my bookings\" — see all your tickets\n"
            "→ \"cancel my booking\" — cancel a flight\n"
            "→ \"update my flight\" — change date/route\n\n"
            "👤 **Profile**\n"
            "→ \"update my email\" — change email\n"
            "→ \"change my phone\" — update phone number\n"
            "→ \"update my name\" — change your name\n"
            "→ \"update my address\" — change address\n\n"
            "📋 **Information**\n"
            "→ \"baggage policy\" — bag allowances\n"
            "→ \"cancellation policy\" — refund rules\n"
            "→ \"change fee\" — modification charges\n\n"
            "Just type naturally — I'll understand!"
        )

    if intent == "thanks":
        return text(f"You're welcome, {first}! ✈️ Is there anything else I can help you with?")

    if intent == "bye":
        return text(f"Goodbye, {first}! Safe travels! ✈️ Have a wonderful journey with Jahan Chatbot Airlines!")

    if intent == "show_bookings":
        result = get_user_bookings(user_id)
        if not result["bookings"]:
            return text("You don't have any bookings yet. Type **book a flight** to make your first booking!")
        tickets = [ticket_response(b) for b in result["bookings"]]
        return {"type": "bookings", "bookings": tickets,
                "message": f"Here are your bookings, {first}:"}

    if intent == "create_booking":
        set_session(user_id, "booking_origin", {})
        return text(
            f"Let's book your flight! ✈️\n\n"
            f"Enter your **departure airport code**:\n"
            f"*(e.g. DEL=Delhi, BOM=Mumbai, BLR=Bangalore, NYC=New York, LHR=London)*"
        )

    if intent == "cancel_booking":
        set_session(user_id, "cancel_pnr", {})
        return text(
            "I'll help you cancel your booking.\n\n"
            "Please enter your **PNR number**:\n"
            "*(You can find it on your boarding pass, e.g. JHAN-A1B2C)*"
        )

    if intent == "update_journey":
        set_session(user_id, "update_journey_pnr", {})
        return text("Let's update your journey details.\n\nPlease enter your **PNR number**:")

    if intent == "update_profile":
        # Check if specific field mentioned in the message itself
        msg_lower = msg.lower()
        direct_map = {
            "email": "email", "mail": "email",
            "phone": "phone", "number": "phone", "contact": "phone", "mobile": "phone",
            "name": "full_name", "full name": "full_name",
            "address": "address"
        }
        detected = None
        for kw, field in direct_map.items():
            if kw in msg_lower:
                detected = field
                break
        if detected:
            set_session(user_id, "update_profile_value", {"field": detected})
            labels = {"full_name": "full name", "email": "email address", "phone": "phone number", "address": "address"}
            return text(f"Please enter your **new {labels.get(detected, detected)}**:")
        # Otherwise ask which field
        set_session(user_id, "update_profile_field", {})
        return text("What would you like to update?\n\n- **name**\n- **email**\n- **phone**\n- **address**\n\nJust type one of the above.")

    if intent == "policy":
        topic = detect_policy_topic(msg)
        result = lookup_policy(topic)
        if result["success"]:
            return {"type": "policies", "policies": result["policies"],
                    "message": "Here is the policy information you requested:"}
        return text("I couldn't find a specific policy for that. Try asking about:\n- **baggage policy**\n- **cancellation policy**\n- **refund policy**\n- **change fee**")

    # Unknown
    return text(
        f"I'm not quite sure what you mean. Here are some things you can try:\n\n"
        f"→ \"book a flight\"\n"
        f"→ \"my bookings\"\n"
        f"→ \"cancel my booking\"\n"
        f"→ \"update my flight\"\n"
        f"→ \"update my email\"\n"
        f"→ \"baggage policy\"\n\n"
        f"Or type **help** to see all options."
    )


# ── PATCH: Override detect_intent with priority-aware version ─────────────────
def detect_intent(msg: str) -> str:
    msg_lower = msg.lower().strip()

    # PRIORITY ORDER: more specific intents first
    PRIORITY_INTENTS = [
        # Cancel must come before show_bookings
        ("cancel_booking", ["cancel my booking", "cancel booking", "cancel my flight",
                            "cancel ticket", "i want to cancel", "cancel reservation",
                            "cancel my ticket"]),
        # Update journey before show_bookings
        ("update_journey", ["update my flight", "change my flight", "update journey",
                            "change destination", "change source", "change date",
                            "modify flight", "update booking", "change my booking",
                            "edit flight", "reschedule", "change my trip",
                            "update my trip", "modify booking", "change origin",
                            "change travel date", "change my destination", "change my source"]),
        # Update profile
        ("update_profile", ["update my name", "change my name", "update email",
                            "change email", "update phone", "change phone",
                            "update contact", "update my address", "change address",
                            "edit profile", "update profile", "change my details",
                            "update my details", "edit my details", "change my email",
                            "change my phone", "update my email", "update my phone",
                            "change number", "update number", "edit contact",
                            "change my number", "update my number", "change my contact"]),
        # Show bookings
        ("show_bookings", ["my bookings", "my flights", "my tickets", "show bookings",
                           "view bookings", "check booking", "booking status",
                           "my reservations", "see my bookings", "list bookings",
                           "all bookings", "what are my bookings", "my trips",
                           "show my bookings", "view my bookings"]),
        # Create booking
        ("create_booking", ["book a flight", "book flight", "new booking",
                            "reserve a flight", "i want to fly", "book ticket",
                            "purchase ticket", "buy ticket", "i want to book",
                            "make a booking", "flight booking", "book a ticket",
                            "i need a flight", "plan a flight", "i want to book a flight"]),
        # Policy
        ("policy", ["baggage policy", "luggage policy", "bag allowance",
                    "cancellation policy", "refund policy", "change fee policy",
                    "no show policy", "check-in policy", "what is the baggage",
                    "how much baggage", "baggage limit", "can i cancel",
                    "refund rules", "cancellation rules", "what are the rules",
                    "policy", "policies", "baggage allowance", "luggage allowance",
                    "carry on", "checked bag", "excess baggage"]),
        # Greetings
        ("greeting", ["hello", "hi", "hey", "good morning", "good evening",
                      "good afternoon", "greetings", "hii", "helo", "hiya", "howdy"]),
        # Help
        ("help", ["help", "what can you do", "how to use", "assist me",
                  "what are the options", "menu", "guide", "commands"]),
        # Thanks
        ("thanks", ["thank you", "thanks", "thank u", "thx", "ty", "appreciated"]),
        # Bye
        ("bye", ["bye", "goodbye", "see you", "later", "take care", "exit", "quit"]),
    ]

    for intent, keywords in PRIORITY_INTENTS:
        for kw in keywords:
            if kw in msg_lower:
                return intent
    return "unknown"
