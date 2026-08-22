import os
from pathlib import Path

from google import genai


def main():
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    client = genai.Client(api_key=api_key)

    prompt = """
You are a professional Computer Science and IT content writer for LinkedIn.

Create ONE original LinkedIn post for a professional IT audience.

Choose ONE useful topic from:
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

Requirements:
- Professional and natural English.
- Educational and technically useful.
- Start with a strong but natural hook.
- Explain one practical technical concept.
- Include 3 to 5 short practical points.
- End with one simple question that encourages discussion.
- Add 3 to 5 relevant hashtags.
- Do not mention AI.
- Do not say that the post was generated.
- Do not use excessive emojis.
- Do not use clickbait.
- Do not invent statistics or fake facts.
- Maximum 1800 characters.
- Return ONLY the final LinkedIn post.
"""

    print("Generating LinkedIn post with Gemini...")

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
    )

    post = (response.text or "").strip()

    if not post:
        raise RuntimeError("Gemini returned an empty post.")

    Path("linkedin_post.txt").write_text(
        post,
        encoding="utf-8"
    )

    print("POST_GENERATION_SUCCESS")
    print(post)


if __name__ == "__main__":
    main()
