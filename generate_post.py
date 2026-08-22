import json
import os
from pathlib import Path

from google import genai


HISTORY_FILE = Path("topics_history.json")
POST_FILE = Path("linkedin_post.txt")
CURRENT_TOPIC_FILE = Path("current_topic.txt")


def load_history():
    if not HISTORY_FILE.exists():
        return []

    try:
        data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_history(history):
    HISTORY_FILE.write_text(
        json.dumps(history, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main():
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    client = genai.Client(api_key=api_key)

    history = load_history()
    history_text = "\n".join(f"- {topic}" for topic in history[-50:])

    prompt = f"""
You are a professional Computer Science and IT content writer for LinkedIn.

Choose ONE NEW technical topic and write one LinkedIn post.

Previously used topics:
{history_text if history_text else "- No previous topics yet."}

The new topic must be clearly different from all previous topics.

Possible areas:
- Computer Science
- IT Support
- Systems Administration
- Networking
- Cybersecurity
- Cloud Computing
- Microsoft 365
- Linux
- Virtualization
- DevOps
- IT Infrastructure
- Databases
- Automation
- AI fundamentals

Return EXACTLY:

TOPIC: <short topic title>

POST:
<final LinkedIn post>

Requirements:
- Professional and natural English.
- Educational and technically useful.
- Strong but natural opening.
- Include 3 to 5 practical points.
- End with one simple question.
- Add 3 to 5 relevant hashtags.
- No excessive emojis.
- No clickbait.
- Do not mention AI.
- Do not claim the post was generated.
- Do not invent statistics or fake facts.
- Maximum 1800 characters.
"""

    print("Generating a new LinkedIn topic and post...")

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
    )

    text = (response.text or "").strip()

    if not text:
        raise RuntimeError("Gemini returned an empty response.")

    if "TOPIC:" not in text or "POST:" not in text:
        raise RuntimeError("Gemini returned an unexpected format.")

    topic_part, post_part = text.split("POST:", 1)

    topic = topic_part.replace("TOPIC:", "").strip()
    post = post_part.strip()

    if not topic:
        raise RuntimeError("No topic was generated.")

    if not post:
        raise RuntimeError("No LinkedIn post was generated.")

    normalized_history = {item.strip().lower() for item in history}

    if topic.lower() in normalized_history:
        raise RuntimeError(f"Duplicate topic generated: {topic}")

    history.append(topic)

    save_history(history)

    POST_FILE.write_text(post, encoding="utf-8")
    CURRENT_TOPIC_FILE.write_text(topic, encoding="utf-8")

    print("TOPIC_GENERATION_SUCCESS")
    print(f"Topic: {topic}")
    print("POST_GENERATION_SUCCESS")
    print(post)


if __name__ == "__main__":
    main()
