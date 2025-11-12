import os
import requests
from dotenv import load_dotenv

load_dotenv()

SN_INSTANCE = os.getenv("SN_INSTANCE")  # e.g. dev313676
SN_USER = os.getenv("SN_USER")
SN_PASS = os.getenv("SN_PASS")

BASE_URL = f"https://{SN_INSTANCE}.service-now.com/api/now/table/u_autosys_changes"


def create_record(job, action, result):
    """Creates a new record in the u_autosys_changes table."""
    payload = {
        "u_job_name": job,
        "u_action": action,
        "u_status": "RUNNING",
        "u_description": f"Action {action} executed on {job}",
        "u_result": result,
        "u_closed": False,  # ✅ Boolean not string
        "u_work_notes": f"{action} started for {job}"
    }

    print("[SNOW CREATE]", payload)
    res = requests.post(BASE_URL, auth=(SN_USER, SN_PASS), json=payload)
    print("[SNOW CREATE RESPONSE]", res.status_code, res.text)

    if res.status_code == 201:
        data = res.json()
        return data["result"]["sys_id"]
    else:
        print("[SNOW CREATE ERROR]", res.text)
        return None


def close_record(record_id, final_status="SUCCESS"):
    """Closes a specific record in ServiceNow."""
    payload = {
        "u_status": final_status,
        "u_closed": True,  # ✅ Proper boolean
        "u_work_notes": f"Job completed successfully with status {final_status}. Auto-closed by AutoSys Bot."
    }

    url = f"{BASE_URL}/{record_id}"
    print("[SNOW CLOSE]", payload)

    res = requests.patch(url, auth=(SN_USER, SN_PASS), json=payload)
    print("[SNOW CLOSE RESPONSE]", res.status_code, res.text)
    return res.status_code