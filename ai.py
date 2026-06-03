import json
import os
from dotenv import load_dotenv
import requests

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def _call_groq(prompt):
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY environment variable is not set.")

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.3,
        "max_tokens": 900
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        response = requests.post(GROQ_URL, json=payload, headers=headers, timeout=60)
        if response.status_code != 200:
            raise RuntimeError(f"Groq API HTTP error {response.status_code}: {response.text}")
        return response.json()
    except requests.RequestException as exc:
        raise RuntimeError(f"Groq API request failed: {str(exc)}") from exc


def analyze_resume(resume_text, user_goal):
    prompt = f"""
You are a senior software engineer and hiring manager.

Evaluate the resume based on the user's goal.

user goal: \"{user_goal}\"

STRICT RULES
- Extract only relevant skills for this goal
- REMOVE irrelevant tools [excel for backend, etc]
- Identify real gaps
- Generate roadmap only for missing fields
- Make output different based on goal

Return only JSON (ensure all arrays contain ONLY strings, no objects or dicts):
{{
  "skills": ["string", "string"],
  "missing_skills": ["string", "string"],
  "roadmap": ["string", "string"],
  "interview_questions": ["string", "string"]
}}

Resume:
{resume_text}
"""
    if not GROQ_API_KEY:
        return {
            "skills": ["Python", "Flask", "SQLAlchemy"],
            "missing_skills": ["Groq API key not configured"],
            "roadmap": [
                "Set GROQ_API_KEY in your .env file",
                "Add real AI analysis once the key is available"
            ],
            "interview_questions": [
                "How would you design a resume analyzer service?",
                "Explain how you use Flask and SQLAlchemy together."
            ],
            "info": "Using local fallback mode because GROQ_API_KEY is missing."
        }

    try:
        response = _call_groq(prompt)
        choices = response.get("choices", [])
        if not choices:
            raise ValueError("Groq API returned no outputs")

        first_choice = choices[0]
        text = first_choice.get("message", {}).get("content", "")

        text = text.strip()
        # Clean up any potential markdown wrappers just in case
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        return json.loads(text)
    except Exception as e:
        return {
            "skills": [],
            "missing_skills": [],
            "roadmap": [],
            "interview_questions": [],
            "error": str(e)
        }
