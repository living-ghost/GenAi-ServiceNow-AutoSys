import os
import requests

from dotenv import load_dotenv

load_dotenv()

SN_INSTANCE = os.getenv("SN_INSTANCE")
SN_USER = os.getenv("SN_USER")
SN_PASS = os.getenv("SN_PASS")

BASE_URL = f"https://{SN_INSTANCE}.service-now.com/api/now/table/u_autosys_changes"


def create_record(job, action, result):
    payload = {
        "u_job_name": job,
        "u_action": action,
        "u_status": "RUNNING",
        "u_description": f"Action {action} executed",
        "u_result": result,
        "u_closed": "false",
        "u_work_notes": f"{action} started for {job}"
    }

    print("[SNOW CREATE]", payload)

    res = requests.post(
        BASE_URL,
        auth=(SN_USER, SN_PASS),
        json=payload
    )

    print("[SNOW CREATE RESPONSE]", res.status_code, res.text)

    data = res.json()
    return data["result"]["sys_id"]


def close_record(record_id):
    payload = {
        "u_status": "SUCCESS",
        "u_closed": "true",
        "u_work_notes": "Job completed, record auto-closed"
    }

    url = f"{BASE_URL}/{record_id}"

    print("[SNOW CLOSE]", payload)

    res = requests.patch(
        url,
        auth=(SN_USER, SN_PASS),
        json=payload
    )

    print("[SNOW CLOSE RESPONSE]", res.status_code, res.text)