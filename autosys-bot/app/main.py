from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every

from app.autosys_simulator import AutosysSimulator
from app.gpt_parser import parse_command
from app.servicenow import create_record, close_record


app = FastAPI()
autosys = AutosysSimulator()


# ✅ Scheduler → Auto-close completed jobs
@app.on_event("startup")
@repeat_every(seconds=3)
def auto_close_scheduler():
    print("[SCHEDULER] Checking all jobs…")

    for job_name, job_data in autosys.jobs.items():
        status = job_data["status"]
        record = job_data["record"]

        print(f"[CHECK] Job={job_name}, Status={status}, Record={record}")

        if status == "SUCCESS" and record is not None:
            print(f"[AUTO] Closing record {record} for job {job_name}")
            close_record(record)
            autosys.jobs[job_name]["record"] = None  # avoids duplicate closing


@app.post("/chat")
async def chat(message: dict):
    user_msg = message["msg"]

    parsed = await parse_command(user_msg)
    action = parsed["action"]
    job = parsed["job_name"]

    try:
        result = getattr(autosys, action)(job)

        # ✅ Create record in custom table
        record_id = create_record(job, action, result)

        autosys.jobs[job]["record"] = record_id

        return {
            "status": "success",
            "result": result,
            "record": record_id
        }

    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }
