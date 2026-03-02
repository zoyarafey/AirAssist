from utils.csv_handler import append_row
from utils.helpers import now_str
import json

def audit_log(user_id: str, action: str, object_type: str, object_id: str,
              input_data: dict, result: dict, status: str):
    record = {
        "timestamp": now_str(),
        "user_id": user_id,
        "action": action,
        "object_type": object_type,
        "object_id": object_id,
        "input": json.dumps(input_data),
        "result": json.dumps(result)[:500],
        "status": status
    }
    try:
        append_row("audit_log.csv", record)
    except Exception as e:
        print(f"Audit log error: {e}")
