# ============================================
# MODULE 8: GITHUB UPLOADER
# Video ko GitHub Releases mein upload karta hai
# Laptop watcher yahan se detect karega
# ============================================

import os
import sys
import requests
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GITHUB_TOKEN, GITHUB_REPO


def create_github_release(tag_name, release_name, body=""):
    """GitHub pe naya release create karta hai."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/releases"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "tag_name": tag_name,
        "name": release_name,
        "body": body,
        "draft": False,
        "prerelease": False
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        return response.json()
    else:
        print(f"❌ Release create error: {response.status_code} - {response.text}")
        return None


def upload_video_to_release(release_id, video_path):
    """Video file ko release mein upload karta hai."""
    filename = os.path.basename(video_path)
    upload_url = f"https://uploads.github.com/repos/{GITHUB_REPO}/releases/{release_id}/assets?name={filename}"

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Content-Type": "video/mp4"
    }

    file_size = os.path.getsize(video_path) / (1024 * 1024)
    print(f"  📤 Uploading: {filename} ({file_size:.1f} MB)")

    with open(video_path, "rb") as f:
        response = requests.post(upload_url, headers=headers, data=f, timeout=300)

    if response.status_code == 201:
        asset = response.json()
        download_url = asset.get("browser_download_url", "")
        print(f"  ✅ Upload complete: {download_url}")
        return download_url
    else:
        print(f"  ❌ Upload error: {response.status_code}")
        return None


def upload_video(video_path, news_title=""):
    """
    Video ko GitHub Release mein upload karta hai.
    Returns: download URL
    """
    if not os.path.exists(video_path):
        print(f"❌ Video file nahi mili: {video_path}")
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    tag_name = f"video-{timestamp}"
    release_name = f"News Video - {timestamp}"
    body = f"Auto generated news video\nTitle: {news_title}\nTime: {timestamp}"

    print(f"\n📤 GitHub Release pe upload ho raha hai...")

    # Release create karo
    release = create_github_release(tag_name, release_name, body)
    if not release:
        return None

    release_id = release["id"]

    # Video upload karo
    download_url = upload_video_to_release(release_id, video_path)
    return download_url


if __name__ == "__main__":
    print("GitHub Uploader ready!")
    print(f"Repo: {GITHUB_REPO}")
