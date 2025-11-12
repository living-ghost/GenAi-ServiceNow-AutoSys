import threading
import time

class AutosysSimulator:

    def __init__(self):
        # job_name → {"status": "RUNNING/SUCCESS/ON_HOLD/ON_ICE", "record": "sys_id"}
        self.jobs = {}

    def force_start(self, job_name):
        """Simulate force start of job."""
        self.jobs[job_name] = {"status": "RUNNING", "record": None}
        threading.Thread(target=self.auto_complete_job, args=(job_name,), daemon=True).start()
        return f"Job {job_name} started successfully"

    def on_hold(self, job_name):
        """Simulate job placed on hold, then auto-complete."""
        self.jobs[job_name] = {"status": "ON_HOLD", "record": None}
        threading.Thread(target=self.auto_complete_job, args=(job_name,), daemon=True).start()
        return f"Job {job_name} is now ON_HOLD and will auto-complete shortly"

    def off_hold(self, job_name):
        """Simulate job removed from hold, then auto-complete."""
        self.jobs[job_name] = {"status": "RUNNING", "record": None}
        threading.Thread(target=self.auto_complete_job, args=(job_name,), daemon=True).start()
        return f"Job {job_name} removed from HOLD and restarted"

    def on_ice(self, job_name):
        """Simulate job put on ice, then auto-complete."""
        self.jobs[job_name] = {"status": "ON_ICE", "record": None}
        threading.Thread(target=self.auto_complete_job, args=(job_name,), daemon=True).start()
        return f"Job {job_name} is now ON_ICE and will auto-complete shortly"

    def off_ice(self, job_name):
        """Simulate job removed from ice, then auto-complete."""
        self.jobs[job_name] = {"status": "RUNNING", "record": None}
        threading.Thread(target=self.auto_complete_job, args=(job_name,), daemon=True).start()
        return f"Job {job_name} removed from ICE and restarted"

    def status(self, job_name):
        """Return current status of a job."""
        if job_name not in self.jobs:
            return f"No such job {job_name}"
        return f"{job_name} → {self.jobs[job_name]['status']}"

    def auto_complete_job(self, job_name):
        """Automatically mark job as SUCCESS after delay."""
        time.sleep(5)  # simulate job run time
        if job_name in self.jobs and self.jobs[job_name]["status"] != "SUCCESS":
            self.jobs[job_name]["status"] = "SUCCESS"
            print(f"[SIM] Job {job_name} auto-completed → SUCCESS")
