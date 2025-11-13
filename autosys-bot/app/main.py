from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from app.autosys_simulator import AutosysSimulator
from app.servicenow import create_record, close_record
from app.gpt_parser import parse_command
from app.job_validator import job_exists, user_can_run_job, user_exists

app = FastAPI()
autosys = AutosysSimulator()

@app.on_event("startup")
@repeat_every(seconds=30)
def auto_close_checker():
    print("[SCHEDULER] Checking all jobs…")
    for job_name, job_data in autosys.jobs.items():
        status = job_data.get("status")
        record = job_data.get("record")

        # Close when job completes successfully
        if status == "SUCCESS" and record:
            print(f"[AUTO] Closing main record {record} — Job {job_name} done")
            close_record(record)
            autosys.jobs[job_name]["record"] = None


@app.post("/chat")
async def chat(message: dict):
    user_msg = message["msg"]
    username = message.get("user", "unknown_user")

    parsed = await parse_command(user_msg)
    actions_list = parsed["actions"]

    results = []
    jobs_involved = set()

    # Validate and execute each job
    for action_item in actions_list:
        action = action_item["action"]
        job = action_item["job_name"]

        # Collect involved jobs
        jobs_involved.add(job)

        # Validate job & user
        if not job_exists(job):
            return {"status": "failed", "error": f"Job '{job}' not found"}

        if not user_exists(username):
            return {"status": "failed", "error": f"User '{username}' not registered"}

        if not user_can_run_job(username, job):
            return {"status": "failed",
                    "error": f"User '{username}' not authorized for {job}"}

        # Run AutoSys command
        result = getattr(autosys, action)(job)
        results.append({"job": job, "action": action, "result": result})

    # Create a SINGLE ServiceNow record
    record_id = create_record(
        job=" ,".join(jobs_involved),
        action="multiple",
        result=str(results)
    )

    # Map ServiceNow record to each job to autoclose later
    for job in jobs_involved:
        autosys.jobs[job]["record"] = record_id

    return {
        "status": "success",
        "user": username,
        "actions_executed": results,
        "record_id": record_id
    }
