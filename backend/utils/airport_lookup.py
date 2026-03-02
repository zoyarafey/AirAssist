import csv
import os
import re

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

# ── Load airports into memory once at startup ──────────────────────────────────
_airports = []
_lookup_index = {}  # maps lowercase key → list of matching airport dicts

def _load():
    global _airports, _lookup_index
    path = os.path.join(DATA_DIR, "airports.csv")
    if not os.path.exists(path):
        return
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        _airports = [dict(row) for row in reader]

    for airport in _airports:
        code = airport["airport_code"].strip().upper()
        city = airport["city"].strip().lower()
        name = airport["airport_name"].strip().lower()
        aliases = [a.strip().lower() for a in airport.get("aliases", "").split("|") if a.strip()]

        # Index by code, city, airport name, and all aliases
        for key in [code.lower(), city, name] + aliases:
            if key not in _lookup_index:
                _lookup_index[key] = []
            if airport not in _lookup_index[key]:
                _lookup_index[key].append(airport)

_load()

# ── Fuzzy match: simple character-level similarity ─────────────────────────────
def _similarity(a: str, b: str) -> float:
    a, b = a.lower().strip(), b.lower().strip()
    if a == b:
        return 1.0
    if a in b or b in a:
        return 0.85
    # Count matching characters
    matches = sum(1 for c in a if c in b)
    return matches / max(len(a), len(b), 1)

# ── Normalize input: remove punctuation, lowercase ────────────────────────────
def _normalize(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^\w\s]", "", text)   # remove punctuation
    text = re.sub(r"\s+", " ", text)       # collapse spaces
    return text

# ── Main resolve function ──────────────────────────────────────────────────────
def resolve_airport(user_input: str) -> dict:
    """
    Takes any user input (code, city, airport name, alias, typo)
    Returns:
      {"found": True,  "code": "DEL", "airports": [...], "multiple": False}
      {"found": True,  "code": None,  "airports": [...], "multiple": True}   ← multiple airports for city
      {"found": False, "code": None,  "airports": [],    "multiple": False}
    """
    raw = user_input.strip()
    normalized = _normalize(raw)

    # 1. Exact match (code, city, name, alias)
    if normalized in _lookup_index:
        matches = _lookup_index[normalized]
        if len(matches) == 1:
            return {"found": True, "code": matches[0]["airport_code"], "airports": matches, "multiple": False}
        else:
            return {"found": True, "code": None, "airports": matches, "multiple": True}

    # 2. Partial word match — check if any key starts with or contains the input
    partial_matches = []
    for key, airports in _lookup_index.items():
        if normalized in key or key.startswith(normalized):
            for a in airports:
                if a not in partial_matches:
                    partial_matches.append(a)

    if partial_matches:
        # Deduplicate by airport_code
        seen = set()
        unique = []
        for a in partial_matches:
            if a["airport_code"] not in seen:
                seen.add(a["airport_code"])
                unique.append(a)
        if len(unique) == 1:
            return {"found": True, "code": unique[0]["airport_code"], "airports": unique, "multiple": False}
        else:
            return {"found": True, "code": None, "airports": unique, "multiple": True}

    # 3. Fuzzy match — find best scoring airport
    best_score = 0.0
    best_matches = []
    THRESHOLD = 0.65

    for key, airports in _lookup_index.items():
        score = _similarity(normalized, key)
        if score >= THRESHOLD:
            if score > best_score:
                best_score = score
                best_matches = list(airports)
            elif score == best_score:
                for a in airports:
                    if a not in best_matches:
                        best_matches.append(a)

    if best_matches:
        seen = set()
        unique = []
        for a in best_matches:
            if a["airport_code"] not in seen:
                seen.add(a["airport_code"])
                unique.append(a)
        if len(unique) == 1:
            return {"found": True, "code": unique[0]["airport_code"], "airports": unique, "multiple": False}
        else:
            return {"found": True, "code": None, "airports": unique, "multiple": True}

    # 4. Nothing found
    return {"found": False, "code": None, "airports": [], "multiple": False}


def format_airport_options(airports: list) -> str:
    """Formats multiple airports into a numbered list for the user."""
    lines = []
    for i, a in enumerate(airports, 1):
        lines.append(f"**{i}.** {a['airport_code']} — {a['airport_name']}, {a['city']}")
    return "\n".join(lines)
