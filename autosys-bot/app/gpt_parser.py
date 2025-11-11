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
    system_prompt = """
    You are an AutoSys command parser.
    Return ONLY valid JSON in this format:

    {
        "action": "force_start | on_ice | off_ice | on_hold | off_hold | status",
        "job_name": "string"
    }

    Rules:
    - No markdown
    - No code blocks
    - No explanation
    """

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

    start = raw.find("{")
    end = raw.rfind("}") + 1

    cleaned = raw[start:end]
    return json.loads(cleaned)
