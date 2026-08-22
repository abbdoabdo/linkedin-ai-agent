import os
from pathlib import Path

from huggingface_hub import InferenceClient


def main():
    token = os.environ.get("HF_TOKEN")

    if not token:
        raise RuntimeError("HF_TOKEN is not configured.")

    client = InferenceClient(
        provider="publicai",
        api_key=token,
    )

    prompt = """
You are a professional Computer Science and IT content writer for LinkedIn.

Create ONE original LinkedIn post for an IT professional audience.

Choose ONE useful Computer Science, IT Support, Systems, Networking,
Cybersecurity, Cloud, Microsoft 365, Linux, Virtualization, or DevOps topic.

Requirements:
- Professional and natural English.
- Suitable for a technical LinkedIn audience.
- Start with a strong but natural hook.
- Explain one practical and useful technical idea.
- Include 3 to 5 short practical points.
- Make the content educational, not motivational.
- Include a simple question at the end to encourage discussion.
- Add 3 to 5 relevant hashtags.
- Do not mention AI.
- Do not say that the post was generated.
- Do not use excessive emojis.
- Do not use clickbait.
- Do not invent statistics or fake facts.
- Maximum 1800 characters.
- Return ONLY the final LinkedIn post.
"""

    print("Generating LinkedIn post...")

    result = client.chat.completions.create(
        model="swiss-ai/Apertus-8B-Instruct-2509",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a professional Computer Science and IT "
                    "LinkedIn content writer."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        max_tokens=800,
        temperature=0.8,
    )

    post = result.choices[0].message.content.strip()

    if not post:
        raise RuntimeError("The model returned an empty post.")

    output_file = Path("linkedin_post.txt")
    output_file.write_text(post, encoding="utf-8")

    print("POST_GENERATION_SUCCESS")
    print(post)


if __name__ == "__main__":
    main()
