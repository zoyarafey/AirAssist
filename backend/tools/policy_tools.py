from utils.csv_handler import read_csv
from datetime import datetime

def lookup_policy(topic: str = "", fare_class: str = None,
                  scope_type: str = None, scope_value: str = None) -> dict:
    policies = read_csv("policies.csv")
    today = datetime.today().date()
    results = []
    topic_lower = topic.lower().strip()

    for p in policies:
        # Check effective dates
        try:
            eff_from = datetime.strptime(p["effective_from"], "%Y-%m-%d").date()
            eff_to = datetime.strptime(p["effective_to"], "%Y-%m-%d").date()
            if not (eff_from <= today <= eff_to):
                continue
        except:
            pass

        # FIX 3: if no topic given, only return first policy of each topic
        # (prevents dumping all 15 policies at once as unstructured text)
        if not topic_lower:
            # Return one representative policy per topic
            if not any(r["topic"] == p["topic"] for r in results):
                results.append(p)
            continue

        # Match topic
        if topic_lower not in p["topic"].lower():
            continue

        # Match fare class if provided
        if fare_class and p["fare_class"] not in [fare_class, "all"]:
            continue

        results.append(p)

    if not results:
        return {"success": False, "message": "No policy found for that query."}
    return {"success": True, "policies": results}


# FIX 3: expanded keyword map so baggage/refund/check-in all map to correct topic
KEYWORD_POLICY_MAP = {
    "baggage": "baggage",
    "luggage": "baggage",
    "bag": "baggage",
    "carry": "baggage",
    "checked bag": "baggage",
    "excess": "baggage",
    "carry on": "baggage",
    "cabin bag": "baggage",
    "cancel": "cancellation",
    "cancellation": "cancellation",
    "refund": "refund",
    "money back": "refund",
    "get my money": "refund",
    "no show": "no_show",
    "no-show": "no_show",
    "missed flight": "no_show",
    "missed": "no_show",
    "change fee": "change_fee",
    "change my ticket": "change_fee",
    "modify": "change_fee",
    "reschedule fee": "change_fee",
    "check-in": "cancellation",
    "check in": "cancellation",
    "checkin": "cancellation",
    "when to arrive": "cancellation",
}

def detect_policy_topic(message: str) -> str:
    msg = message.lower()
    for kw, topic in KEYWORD_POLICY_MAP.items():
        if kw in msg:
            return topic
    return ""
