import csv
import os
import threading
from typing import List, Dict, Optional

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
_write_lock = threading.Lock()

def get_path(filename: str) -> str:
    return os.path.join(DATA_DIR, filename)

def read_csv(filename: str) -> List[Dict]:
    path = get_path(filename)
    if not os.path.exists(path):
        return []
    # FIX 1: open with newline='' so csv module handles \r\n and \n uniformly
    with open(path, "r", newline="", encoding="utf-8") as f:
        return [dict(row) for row in csv.DictReader(f)]

def write_csv(filename: str, rows: List[Dict], fieldnames: Optional[List[str]] = None):
    if not rows and not fieldnames:
        return
    path = get_path(filename)
    fields = fieldnames or list(rows[0].keys())
    with _write_lock:
        # newline='' required by csv module to prevent double \r\n on Windows
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

def append_row(filename: str, row: Dict):
    path = get_path(filename)
    file_exists = os.path.exists(path) and os.path.getsize(path) > 0

    if file_exists:
        # FIX 1: read existing header to ensure column order matches exactly
        # This prevents column mismatch when new user dict has different key order
        with open(path, "r", newline="", encoding="utf-8") as f:
            existing_fields = next(csv.reader(f))
        with _write_lock:
            with open(path, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=existing_fields)
                # Fill any missing fields with empty string
                filled_row = {k: row.get(k, "") for k in existing_fields}
                writer.writerow(filled_row)
    else:
        with _write_lock:
            with open(path, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(row.keys()))
                writer.writeheader()
                writer.writerow(row)

def find_one(filename: str, key: str, value: str) -> Optional[Dict]:
    for row in read_csv(filename):
        if row.get(key, "").strip().lower() == value.strip().lower():
            return row
    return None

def find_many(filename: str, key: str, value: str) -> List[Dict]:
    return [r for r in read_csv(filename) if r.get(key,"").strip().lower() == value.strip().lower()]

def update_one(filename: str, key: str, value: str, updates: Dict) -> bool:
    rows = read_csv(filename)
    updated = False
    for row in rows:
        if row.get(key,"").strip().lower() == value.strip().lower():
            row.update(updates)
            updated = True
            break
    if updated:
        write_csv(filename, rows)
    return updated
