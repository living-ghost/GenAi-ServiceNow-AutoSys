import threading
import time

class AutosysSimulator:

    def __init__(self):
        # job_name → {"status": "", "record": ""}
        self.jobs = {}

    def force_start(self, job_name):
        self.jobs[job_name] = {"status": "RUNNING", "record": None}

        # Auto complete after delay
        threading.Thread(target=self.auto_complete_job, args=(job_name,), daemon=True).start()

        return f"Job {job_name} started successfully"

    def on_ice(self, job_name):
        self.jobs[job_name] = {"status": "ON_ICE", "record": None}
        return f"Job {job_name} is now ON_ICE"

    def off_ice(self, job_name):
        self.jobs[job_name] = {"status": "SUCCESS", "record": None}
        return f"Job {job_name} removed from ICE"

    def on_hold(self, job_name):
        self.jobs[job_name] = {"status": "ON_HOLD", "record": None}
        return f"Job {job_name} is now ON_HOLD"

    def off_hold(self, job_name):
        self.jobs[job_name] = {"status": "SUCCESS", "record": None}
        return f"Job {job_name} removed from HOLD"

    def status(self, job_name):
        if job_name not in self.jobs:
            return f"No such job {job_name}"
        return f"{job_name} → {self.jobs[job_name]['status']}"

    def auto_complete_job(self, job_name):
        time.sleep(3)  # simulate work
        if job_name in self.jobs:
            self.jobs[job_name]["status"] = "SUCCESS"
            print(f"[SIM] Job {job_name} auto-completed → SUCCESS")
