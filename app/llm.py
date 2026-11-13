
import os
import json
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from groq import Groq

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

PROMPT_DIR = BASE_DIR / "prompts"

PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()


def load_prompt(filename):
    path = PROMPT_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {filename}"
        )

    return path.read_text(encoding="utf-8")


def call_gemini(prompt):

    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv(
        "GEMINI_MODEL",
        "gemini-3.8-flash"
    )

    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing")

    client = genai.Client(api_key=api_key)

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            if not response.text:
                raise RuntimeError("Gemini returned an empty response")

            return response.text

        except Exception as e:
            message = str(e)

            if "503" in message or "UNAVAILABLE" in message:
                if attempt < 2:
                    time.sleep(2 ** (attempt + 1))
                else:
                    raise RuntimeError(
                        "Gemini is temporarily unavailable"
                    )
            else:
                raise


def call_groq(prompt):

    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv(
        "GROQ_MODEL",
        "llama-3.3-70b-versatile"
    )

    if not api_key:
        raise ValueError("GROQ_API_KEY is missing")

    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format={
            "type": "json_object"
        }
    )

    return response.choices[0].message.content


def parse_response(raw_response):

    try:
        cleaned = raw_response.strip()

        if cleaned.startswith("```"):
            cleaned = cleaned.replace("```json", "", 1)
            cleaned = cleaned.rsplit("```", 1)[0].strip()

        data = json.loads(cleaned)

        answer = data.get("answer", "No answer generated.")
        confidence = str(
            data.get("confidence", "medium")
        ).lower()

        follow_up = data.get("follow_up", "")

        if confidence not in ["high", "medium", "low"]:
            confidence = "medium"

        return {
            "answer": answer,
            "confidence": confidence,
            "follow_up": follow_up
        }

    except (json.JSONDecodeError, AttributeError):
        return {
            "answer": raw_response,
            "confidence": "low",
            "follow_up": "Would you like to ask another question?"
        }


def ask_llm(question, prompt_version=1):

    if prompt_version == 1:
        task_prompt = load_prompt("task_prompt_1.txt")

    elif prompt_version == 2:
        task_prompt = load_prompt("task_prompt_2.txt")

    else:
        raise ValueError("prompt_version must be 1 or 2")

    system_prompt = load_prompt("system_prompt.txt")

    user_prompt = task_prompt.format(
        question=question
    )

    final_prompt = (
        system_prompt
        + "\n\n"
        + user_prompt
    )

    if PROVIDER == "gemini":
        raw_response = call_gemini(final_prompt)

    elif PROVIDER == "groq":
        raw_response = call_groq(final_prompt)

    else:
        raise ValueError(
            "Unsupported provider. Choose gemini or groq."
        )

    return parse_response(raw_response)
