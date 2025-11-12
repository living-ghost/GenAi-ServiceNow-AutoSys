import os
import json
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-02-01"
)

async def parse_command(user_message: str):
    """
    Uses Azure OpenAI to parse a natural language command
    into an action and multiple job names.

    Example:
        Input: "Please force start job alpha, job beta and job gamma"
        Output:
        {
            "action": "force_start",
            "job_names": ["alpha", "beta", "gamma"]
        }
    """

    system_prompt = """
    You are an AutoSys command parser.
    Return ONLY valid JSON (no markdown, no code blocks, no explanation).

    Format:
    {
        "action": "force_start | on_ice | off_ice | on_hold | off_hold | status",
        "job_names": ["job1", "job2", "job3"]
    }

    Rules:
    - Always output JSON only.
    - Extract all mentioned job names (comma or 'and' separated).
    - 'job_names' must always be a list, even if there is only one job.
    - If action not found, return "action": "unknown".
    """

    # 🔹 Call Azure OpenAI
    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0
    )

    raw = response.choices[0].message.content.strip()

    # Cleanup safety
    raw = raw.replace("```", "").replace("json", "").strip()

    # Extract only JSON portion if extra text appears
    start = raw.find("{")
    end = raw.rfind("}") + 1
    cleaned = raw[start:end]

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as e:
        print("[GPT PARSER ERROR] Invalid JSON:", raw)
        raise ValueError(f"Parser failed to produce valid JSON: {e}")

    # Ensure structure validity
    if "job_names" not in parsed:
        parsed["job_names"] = []
    elif isinstance(parsed["job_names"], str):
        parsed["job_names"] = [parsed["job_names"]]

    if "action" not in parsed:
        parsed["action"] = "unknown"

    return parsed
