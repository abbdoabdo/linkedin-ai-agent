import os
from pathlib import Path

from huggingface_hub import InferenceClient

token = os.environ["HF_TOKEN"]

client = InferenceClient(
    provider="auto",
    api_key=token,
)

prompt = """
You are a professional Computer Science and IT LinkedIn content writer.

Create ONE original LinkedIn post for an IT professional audience.

Topic:
Choose one useful Computer Science or IT topic.

Requirements:
- Professional and natural
- Useful and educational
- Suitable for LinkedIn
- Clear English
- Strong opening hook
- 3 to 5 short practical points
- End with a simple question that encourages discussion
- Add 3 to 5 relevant hashtags
- Do not mention AI or that the post was generated
- Do not repeat common generic motivational content
- Do not use excessive emojis
- Maximum 1800 characters

Return ONLY the final LinkedIn post.
"""

print("Generating LinkedIn post...")

result = client.chat.completions.create(
    model="google/gemma-2-2b-it",
    messages=[
        {
            "role": "user",
            "content": prompt,
        }
    ],
    max_tokens=600,
)

post = result.choices[0].message.content.strip()

Path("linkedin_post.txt").write_text(
    post,
    encoding="utf-8"
)

print("POST_GENERATION_SUCCESS")
print(post)
