# ✈️ AirAssist — Airline Chatbot 

A full-stack rule-based airline customer support chatbot with login, flight booking, cancellation, policy lookup, and journey update features.
----
## 🌐 Live Project
Live Frontend: https://air-assist-pink.vercel.app
Backend API: https://airassist.onrender.com

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React.js + Tailwind CSS |
| Backend | Python + FastAPI |
| Database | CSV files (lightweight) |
| Routing | Rule-based Orchestrator (no NLP/LLM) |

---

## 📁 Project Structure

```
airassist/
├── frontend/               # React app
│   ├── src/
│   │   ├── pages/          # Login, Signup, Home, Chat
│   │   ├── components/     # BoardingPass, ChatMessage, Logo
│   │   ├── contexts/       # AuthContext
│   │   ├── services/       # API calls
│   │   └── styles/         # Global CSS
│   ├── package.json
│   └── vite.config.js
│
└── backend/                # FastAPI app
    ├── main.py             # Entry point + routes
    ├── auth.py             # Login/Signup logic
    ├── orchestrator.py     # Intent detection + tool routing
    ├── tools/
    │   ├── booking_tools.py    # Book, cancel, update flights
    │   ├── policy_tools.py     # Policy lookup
    │   ├── customer_tools.py   # Profile updates
    │   ├── validation.py       # Input validation
    │   └── logger.py           # Audit trail
    ├── data/               # CSV database files
    └── utils/              # CSV handler, helpers
```


---

## 🔐 Demo Credentials

| Email | Password |
|-------|----------|
| amar.sharma@email.com | password123 |
| priya.mehta@email.com | pass456 |

---

## 💬 Supported Chat Commands

| User Says | Action |
|-----------|--------|
| "book a flight" | Multi-step booking flow |
| "my bookings" | Shows all bookings as boarding passes |
| "cancel my flight" | Cancels booking by PNR |
| "update my flight" | Updates source/destination/date |
| "update my email" | Updates profile details |
| "baggage allowance" | Shows baggage policy |
| "cancellation policy" | Shows refund/cancel policy |
| "check-in policy" | Shows check-in rules |
| "help" | Shows available commands |

---

## 🎫 Features

- **Login & Signup** with CSV-backed authentication
- **Conversational booking** — step-by-step guided flow
- **Real boarding passes** — visual ticket with QR code
- **Booking management** — view, cancel, update flights
- **Policy lookup** — baggage, cancellation, check-in, more
- **Profile updates** — name, email, phone, address
- **Audit trail** — all changes logged to update_history.csv
- **Chat history** — persisted in localStorage
- **Responsive design** — works on mobile and desktop
# AirAssist
