import os
from pathlib import Path

from huggingface_hub import InferenceClient

token = os.environ["HF_TOKEN"]

client = InferenceClient(
    provider="auto",
    api_key=token,
)

prompt = """
Create a professional 16:9 LinkedIn image about Computer Science and IT.

Topic:
Microsoft 365 Security, MFA and Identity Protection.

Style:
- Modern enterprise cybersecurity
- Premium professional LinkedIn design
- Dark navy and blue technology atmosphere
- Authentication and identity security concepts
- Clean composition
- No people
- No copyrighted logos
- Minimal or no text
- Suitable for a professional technology audience
"""

print("Generating image...")

image = client.text_to_image(
    prompt,
    model="black-forest-labs/FLUX.1-schnell",
)

output = Path("linkedin_test_hf.png")
image.save(output)

print(f"Image saved to: {output}")
