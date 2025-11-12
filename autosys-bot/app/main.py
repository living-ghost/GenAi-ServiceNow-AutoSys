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
    action = parsed["action"]
    job_names = parsed["job_names"]

    print(f"[CHAT] {username} triggered '{action}' for jobs: {', '.join(job_names)}")

    # ✅ Validate user existence
    if not user_exists(username):
        return {"status": "failed", "error": f"User '{username}' not registered"}

    # ✅ Validate all jobs
    valid_jobs = []
    invalid_jobs = []
    for job in job_names:
        if not job_exists(job):
            invalid_jobs.append(job)
            continue
        if not user_can_run_job(username, job):
            invalid_jobs.append(job)
            continue
        valid_jobs.append(job)

    if not valid_jobs:
        return {"status": "failed", "error": f"No valid jobs found. Invalid: {invalid_jobs}"}

    # ✅ Create a single ServiceNow record for all valid jobs
    description = f"Action '{action}' executed on jobs: {', '.join(valid_jobs)}"
    result_summary = f"Jobs affected: {len(valid_jobs)}. Invalid: {len(invalid_jobs)}."

    record_id = create_record(
        job=",".join(valid_jobs),
        action=action,
        result=result_summary
    )

    # ✅ Execute the jobs individually
    results = []
    for job in valid_jobs:
        try:
            result = getattr(autosys, action)(job)
            autosys.jobs[job] = {"status": "RUNNING", "record": record_id}
            results.append({"job": job, "status": "success", "result": result})
        except Exception as e:
            results.append({"job": job, "status": "failed", "error": str(e)})

    return {
        "status": "success",
        "action": action,
        "record_id": record_id,
        "user": username,
        "results": results
    }
