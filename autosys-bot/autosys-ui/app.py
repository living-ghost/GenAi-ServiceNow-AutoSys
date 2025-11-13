import streamlit as st
import requests

FASTAPI_URL = "http://127.0.0.1:8000/chat"   # your FastAPI backend

st.set_page_config(page_title="AutoSys Control Panel", layout="wide")

st.title("🤖 AutoSys + ServiceNow Automation Bot")
st.write("Control jobs, validate users, and trigger SNOW records.")

# --- User input section ---
st.subheader("🔐 User Authentication")
username = st.text_input("Enter your username", placeholder="akhil.kaniparampil")

st.subheader("🧠 Command Input")
user_message = st.text_area(
    "Enter command",
    placeholder="Example: please on-hold sample_job_batch_1, sample_job_batch_2 and run sample_job_batch_3",
    height=150
)

if st.button("▶️ Execute Command"):
    if not user_message.strip():
        st.warning("Please enter a command.")
    elif not username.strip():
        st.warning("Please enter username.")
    else:
        payload = {"msg": user_message, "user": username}

        with st.spinner("Processing via LLM and executing AutoSys…"):
            try:
                response = requests.post(FASTAPI_URL, json=payload, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    st.success("Command executed successfully!")

                    st.json(data)

                else:
                    st.error(f"Server error: {response.status_code}")
                    st.text(response.text)

            except Exception as e:
                st.error(f"Error communicating with backend: {e}")

# History section
st.subheader("📜 Command Examples")
st.code("""
Examples you can try:
1. please on hold job sample_job_batch
2. force start job finance_batch
3. on hold job A, job B and force start job C
4. run job payroll_batch and ice job billing_batch
5. remove ice for job order_processing
""")
