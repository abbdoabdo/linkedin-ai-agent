import os
from pathlib import Path

from huggingface_hub import InferenceClient


def main():
    token = os.environ.get("HF_TOKEN")

    if not token:
        raise RuntimeError("HF_TOKEN is not configured.")

    topic_file = Path("current_topic.txt")

    if not topic_file.exists():
        raise RuntimeError("current_topic.txt was not found.")

    topic = topic_file.read_text(encoding="utf-8").strip()

    if not topic:
        raise RuntimeError("Current topic is empty.")

    client = InferenceClient(
        provider="auto",
        api_key=token,
    )

    prompt = f"""
Create a professional 16:9 LinkedIn visual about:

{topic}

Style:
- Modern Computer Science and IT
- Premium professional LinkedIn aesthetic
- Clean enterprise technology design
- Visually explain the main technical concept
- Dark navy and blue technology atmosphere
- Professional and sophisticated
- No people
- No copyrighted logos
- Minimal or no text
- Suitable for an IT professional audience
- The visual must clearly match the topic
"""

    print(f"Generating image for topic: {topic}")
    print("Generating image...")

    image = client.text_to_image(
        prompt,
        model="black-forest-labs/FLUX.1-schnell",
    )

    output = Path("linkedin_test_hf.png")
    image.save(output)

    print("IMAGE_GENERATION_SUCCESS")
    print(f"Image saved to: {output}")


if __name__ == "__main__":
    main()
