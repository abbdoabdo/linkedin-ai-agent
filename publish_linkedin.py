import os
import sys
from pathlib import Path

import requests


ACCESS_TOKEN = os.environ.get("LINKEDIN_ACCESS_TOKEN")

POST_FILE = Path("linkedin_post.txt")
IMAGE_FILE = Path("linkedin_test_hf.png")

LINKEDIN_API = "https://api.linkedin.com"
LINKEDIN_VERSION = "202602"


def fail(message):
    print(f"ERROR: {message}")
    sys.exit(1)


def get_headers():
    if not ACCESS_TOKEN:
        fail("LINKEDIN_ACCESS_TOKEN is not configured.")

    return {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Linkedin-Version": LINKEDIN_VERSION,
    }


def get_member_urn():
    """
    Get the authenticated LinkedIn member ID.

    The access token determines which LinkedIn account
    will be used for publishing.
    """

    url = f"{LINKEDIN_API}/v2/userinfo"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }

    print("Getting authenticated LinkedIn member...")

    response = requests.get(
        url,
        headers=headers,
        timeout=30,
    )

    if response.status_code != 200:
        print(response.text)
        fail(
            f"Could not retrieve LinkedIn member information. "
            f"HTTP {response.status_code}"
        )

    data = response.json()

    member_id = data.get("sub")

    if not member_id:
        print(data)
        fail("LinkedIn member ID was not returned.")

    member_urn = f"urn:li:person:{member_id}"

    print(f"Authenticated member: {member_urn}")

    return member_urn


def register_image_upload(member_urn):
    """
    Register the image upload using the LinkedIn Assets API.
    """

    url = f"{LINKEDIN_API}/v2/assets?action=registerUpload"

    headers = get_headers()
    headers["Content-Type"] = "application/json"

    payload = {
        "registerUploadRequest": {
            "recipes": [
                "urn:li:digitalmediaRecipe:feedshare-image"
            ],
            "owner": member_urn,
            "serviceRelationships": [
                {
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent",
                }
            ],
        }
    }

    print("Registering image upload...")

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=30,
    )

    if response.status_code not in (200, 201):
        print(response.text)
        fail(
            f"Could not register LinkedIn image upload. "
            f"HTTP {response.status_code}"
        )

    data = response.json()

    value = data.get("value", {})

    upload_mechanism = value.get("uploadMechanism", {})

    upload_data = upload_mechanism.get(
        "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
    )

    if not upload_data:
        print(data)
        fail("LinkedIn did not return upload information.")

    upload_url = upload_data.get("uploadUrl")
    asset = value.get("asset")

    if not upload_url:
        print(data)
        fail("LinkedIn upload URL was not returned.")

    if not asset:
        print(data)
        fail("LinkedIn image asset URN was not returned.")

    print(f"Image asset: {asset}")

    return upload_url, asset


def upload_image(upload_url):
    """
    Upload the actual PNG file to LinkedIn.
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
            timeout=120,
        )

    if response.status_code not in (200, 201):
        print(response.text)
        fail(
            f"Image upload failed. "
            f"HTTP {response.status_code}"
        )

    print("IMAGE_UPLOAD_SUCCESS")


def create_post(member_urn, asset_urn, post_text):
    """
    Create a public LinkedIn post containing the generated image.
    """

    url = f"{LINKEDIN_API}/v2/ugcPosts"

    headers = get_headers()
    headers["Content-Type"] = "application/json"

    payload = {
        "author": member_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": post_text
                },
                "shareMediaCategory": "IMAGE",
                "media": [
                    {
                        "status": "READY",
                        "description": {
                            "text": "Professional IT and technology visual"
                        },
                        "media": asset_urn,
                        "title": {
                            "text": "IT & Technology"
                        },
                    }
                ],
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        },
    }

    print("Publishing LinkedIn post...")

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=60,
    )

    if response.status_code != 201:
        print(response.text)
        fail(
            f"LinkedIn post creation failed. "
            f"HTTP {response.status_code}"
        )

    post_id = response.headers.get("X-RestLi-Id")

    print("LINKEDIN_PUBLISH_SUCCESS")

    if post_id:
        print(f"LinkedIn Post ID: {post_id}")

    print("The post was published to the authenticated member profile.")


def main():
    print("========================================")
    print(" LinkedIn Personal Profile Publisher")
    print("========================================")

    if not ACCESS_TOKEN:
        fail("LINKEDIN_ACCESS_TOKEN is not configured.")

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

    if not IMAGE_FILE.exists():
        fail(f"Image file not found: {IMAGE_FILE}")

    member_urn = get_member_urn()

    upload_url, asset_urn = register_image_upload(
        member_urn
    )

    upload_image(upload_url)

    create_post(
        member_urn,
        asset_urn,
        post_text,
    )

    print("========================================")
    print(" LINKEDIN PUBLISH COMPLETED")
    print("========================================")


if __name__ == "__main__":
    main()
