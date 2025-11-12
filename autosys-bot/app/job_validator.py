import os
import pandas as pd

# Get base directory (works even when running uvicorn from anywhere)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def safe_read_excel(file_name):
    file_path = os.path.join(BASE_DIR, file_name)
    if not os.path.exists(file_path):
        print(f"[ERROR] File not found: {file_path}")
        return pd.DataFrame()
    try:
        df = pd.read_excel(file_path)
        print(f"[INFO] Loaded {file_name} with {len(df)} rows")
        return df
    except Exception as e:
        print(f"[ERROR] Could not read {file_name}: {e}")
        return pd.DataFrame()

jobs_df = safe_read_excel("jobs.xlsx")
users_df = safe_read_excel("user_groups.xlsx")

def job_exists(job_name: str) -> bool:
    return not jobs_df.empty and job_name in jobs_df["job_name"].values

def user_exists(username: str) -> bool:
    return not users_df.empty and username in users_df["username"].values

def user_can_run_job(username: str, job_name: str) -> bool:
    if jobs_df.empty or users_df.empty:
        print("[WARN] Excel dataframes are empty.")
        return False
    try:
        job_group = jobs_df.loc[jobs_df["job_name"] == job_name, "group_allowed"].values[0]
        user_group = users_df.loc[users_df["username"] == username, "user_group"].values[0]
        return job_group == user_group
    except IndexError:
        return False
