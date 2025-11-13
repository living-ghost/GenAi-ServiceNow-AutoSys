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

    Understand natural language instructions and extract ALL actions and ALL job names.

    Return ONLY valid JSON in this EXACT format:

    {
        "actions": [
            { "action": "force_start | on_hold | off_hold | on_ice | off_ice | status",
              "job_name": "string"
            }
        ]
    }

    Rules:
    - Convert "run job", "start job" → force_start
    - Convert "hold", "on hold", "put on hold" → on_hold
    - Convert "ice", "on ice" → on_ice
    - Convert "off ice" → off_ice
    - Convert "off hold" → off_hold
    - Do NOT include explanations, code blocks or markdown.
    """

    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0
    )

    content = response.choices[0].message.content.strip()
    content = content.replace("```", "").replace("json", "").strip()

    start = content.find("{")
    end = content.rfind("}") + 1

    return json.loads(content[start:end])
