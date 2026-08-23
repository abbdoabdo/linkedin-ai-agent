import os
import requests

token = os.environ["LINKEDIN_ACCESS_TOKEN"]

response = requests.get(
    "https://api.linkedin.com/v2/me",
    headers={
        "Authorization": f"Bearer {token}",
    },
    timeout=30,
)

print("HTTP STATUS:", response.status_code)
print("RESPONSE:", response.text)
