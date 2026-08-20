import json
from pathlib import Path

from openai import AsyncOpenAI

from app.core.config import settings


client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None


async def transcribe_audio(file_path: str) -> str:
    if not client:
        return "Demo transcript: Team discussed onboarding, release timeline, and client follow-ups. Riya will share the onboarding checklist by Friday. Amit will send the sprint update tomorrow."

    with Path(file_path).open("rb") as audio_file:
        transcript = await client.audio.transcriptions.create(
            model=settings.openai_whisper_model,
            file=audio_file,
            prompt="This is a business meeting between Indian remote team members speaking in Hindi, English, and Hinglish.",
        )
    return transcript.text


async def extract_action_items(transcript: str) -> list[dict]:
    if not client:
        return [
            {
                "task": "Share onboarding checklist",
                "assignee": "Riya",
                "deadline": "Friday",
                "status": "pending",
                "reminder_sent": False,
            },
            {
                "task": "Send sprint update",
                "assignee": "Amit",
                "deadline": "Tomorrow",
                "status": "pending",
                "reminder_sent": False,
            },
        ]

    prompt = f"""
    Extract action items from the following meeting transcript.
    Return strictly valid JSON as an array of objects with keys:
    task, assignee, deadline, status, reminder_sent.
    Rules:
    - status should default to pending unless clearly complete.
    - if deadline is missing, use null.
    - keep concise business wording.
    Transcript:
    {transcript}
    """

    response = await client.chat.completions.create(
        model=settings.openai_action_model,
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You extract structured action items from multilingual Indian team meeting transcripts."},
            {"role": "user", "content": prompt},
        ],
    )
    content = response.choices[0].message.content or '{"items": []}'
    parsed = json.loads(content)
    if isinstance(parsed, list):
        return parsed
    return parsed.get("items", [])
