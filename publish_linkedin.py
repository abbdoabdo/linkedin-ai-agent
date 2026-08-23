
import os
import sys
from pathlib import Path

import requests


# ============================================================
# Configuration
# ============================================================

ACCESS_TOKEN = os.environ.get("LINKEDIN_ACCESS_TOKEN")
PERSON_URN = os.environ.get("LINKEDIN_PERSON_URN")

POST_FILE = Path("linkedin_post.txt")
IMAGE_FILE = Path("linkedin_test_hf.png")

LINKEDIN_API = "https://api.linkedin.com"

# LinkedIn API version
LINKEDIN_VERSION = "202602"


# ============================================================
# Helpers
# ============================================================

def fail(message):
    print(f"ERROR: {message}")
    sys.exit(1)


def get_headers(content_type=True):
    if not ACCESS_TOKEN:
        fail("LINKEDIN_ACCESS_TOKEN is not configured.")

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Linkedin-Version": LINKEDIN_VERSION,
        "X-Restli-Protocol-Version": "2.0.0",
    }

    if content_type:
        headers["Content-Type"] = "application/json"

    return headers


def validate_person_urn():
    """
    Validate the configured LinkedIn Person URN.

    Expected format:

        urn:li:person:XXXXXXXX

    This value must belong to the LinkedIn member
    authenticated by the access token.
    """

    if not PERSON_URN:
        fail(
            "LINKEDIN_PERSON_URN is not configured.\n"
            "Add your personal LinkedIn Person URN as a GitHub Secret."
        )

    if not PERSON_URN.startswith("urn:li:person:"):
        fail(
            "LINKEDIN_PERSON_URN has an invalid format.\n"
            "Expected: urn:li:person:YOUR_PERSON_ID"
        )

    print(f"Using LinkedIn author: {PERSON_URN}")


# ============================================================
# Image Upload
# ============================================================

def initialize_image_upload():
    """
    Initialize an image upload using LinkedIn Images API.

    The returned upload URL is then used to upload
    the generated PNG file.
    """

    url = f"{LINKEDIN_API}/rest/images?action=initializeUpload"

    payload = {
        "initializeUploadRequest": {
            "owner": PERSON_URN
        }
    }

    print("Initializing LinkedIn image upload...")

    response = requests.post(
        url,
        headers=get_headers(),
        json=payload,
        timeout=60,
    )

    if response.status_code not in (200, 201):
        print("LinkedIn response:")
        print(response.text)

        fail(
            "Could not initialize LinkedIn image upload. "
            f"HTTP {response.status_code}"
        )

    try:
        data = response.json()
    except ValueError:
        print(response.text)
        fail("LinkedIn returned an invalid JSON response.")

    value = data.get("value", {})

    upload_url = value.get("uploadUrl")
    image_urn = value.get("image")

    if not upload_url:
        print(data)
        fail("LinkedIn did not return an image upload URL.")

    if not image_urn:
        print(data)
        fail("LinkedIn did not return an image URN.")

    print(f"Image URN: {image_urn}")

    return upload_url, image_urn


def upload_image(upload_url):
    """
    Upload the actual PNG image to LinkedIn.
    """

    if not IMAGE_FILE.exists():
        fail(f"Image file not found: {IMAGE_FILE}")

    print(f"Uploading image: {IMAGE_FILE}")

    with IMAGE_FILE.open("rb") as image_file:
        response = requests.put(
            upload_url,
            headers={
                "Content-Type": "image/png",
            },
            data=image_file,
            timeout=180,
        )

    if response.status_code not in (200, 201):
        print("LinkedIn upload response:")
        print(response.text)

        fail(
            "LinkedIn image upload failed. "
            f"HTTP {response.status_code}"
        )

    print("IMAGE_UPLOAD_SUCCESS")


# ============================================================
# Create LinkedIn Post
# ============================================================

def create_post(post_text, image_urn):
    """
    Create a public LinkedIn post using the current Posts API.

    Endpoint:

        POST https://api.linkedin.com/rest/posts
    """

    url = f"{LINKEDIN_API}/rest/posts"

    payload = {
        "author": PERSON_URN,
        "commentary": post_text,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "content": {
            "media": {
                "title": "IT & Technology",
                "id": image_urn,
            }
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }

    print("Publishing LinkedIn post using Posts API...")

    response = requests.post(
        url,
        headers=get_headers(),
        json=payload,
        timeout=60,
    )

    print(f"LinkedIn HTTP status: {response.status_code}")

    if response.status_code not in (200, 201):
        print("LinkedIn API response:")
        print(response.text)

        fail(
            "LinkedIn post creation failed. "
            f"HTTP {response.status_code}"
        )

    post_id = response.headers.get("X-RestLi-Id")

    print("LINKEDIN_PUBLISH_SUCCESS")

    if post_id:
        print(f"LinkedIn Post ID: {post_id}")

    print("The post was published to the configured personal profile.")


# ============================================================
# Main
# ============================================================

def main():
    print("========================================")
    print(" LinkedIn Personal Profile Publisher")
    print(" Posts API")
    print("========================================")

    # --------------------------------------------------------
    # Validate environment
    # --------------------------------------------------------

    if not ACCESS_TOKEN:
        fail("LINKEDIN_ACCESS_TOKEN is not configured.")

    validate_person_urn()

    # --------------------------------------------------------
    # Validate generated post
    # --------------------------------------------------------

    if not POST_FILE.exists():
        fail(f"Post file not found: {POST_FILE}")

    post_text = POST_FILE.read_text(
        encoding="utf-8"
    ).strip()

    if not post_text:
        fail("linkedin_post.txt is empty.")

    if len(post_text) > 3000:
        fail(
            f"LinkedIn post is too long: "
            f"{len(post_text)} characters."
        )

    # --------------------------------------------------------
    # Validate generated image
    # --------------------------------------------------------

    if not IMAGE_FILE.exists():
        fail(f"Image file not found: {IMAGE_FILE}")

    print(f"Post characters: {len(post_text)}")
    print(f"Image file: {IMAGE_FILE}")
    print(f"Image size: {IMAGE_FILE.stat().st_size} bytes")

    # --------------------------------------------------------
    # Upload image
    # --------------------------------------------------------

    upload_url, image_urn = initialize_image_upload()

    upload_image(upload_url)

    # --------------------------------------------------------
    # Publish post
    # --------------------------------------------------------

    create_post(
        post_text=post_text,
        image_urn=image_urn,
    )

    print("========================================")
    print(" LINKEDIN PUBLISH COMPLETED")
    print("========================================")


if __name__ == "__main__":
    main()
