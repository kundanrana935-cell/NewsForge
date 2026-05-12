# ============================================
# WATCHER.PY - LAPTOP PE CHALTA HAI
# GitHub Releases check karta hai
# Naya video aaya toh C:\NewsVideos\ mein download karta hai
# Windows notification deta hai
# ============================================

import os
import sys
import time
import json
import requests
import threading
from datetime import datetime
from pathlib import Path

# ---- SETTINGS (config se alag hai kyunki laptop pe chalta hai) ----
GITHUB_TOKEN = "your_github_token_here"        # Same token
GITHUB_REPO = "your_username/newsforge-videos"  # Same repo
DOWNLOAD_FOLDER = r"C:\NewsVideos"              # Jahan save hogi
CHECK_INTERVAL = 300                             # Har 5 minute mein check
SEEN_RELEASES_FILE = os.path.join(os.path.expanduser("~"), ".newsforge_seen.json")


def load_seen_releases():
    """Pehle dekhe gaye releases load karta hai."""
    if os.path.exists(SEEN_RELEASES_FILE):
        with open(SEEN_RELEASES_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_seen_releases(seen):
    """Dekhe gaye releases save karta hai."""
    with open(SEEN_RELEASES_FILE, "w") as f:
        json.dump(list(seen), f)


def send_windows_notification(title, message):
    """Windows toast notification bhejta hai."""
    try:
        from winotify import Notification, audio
        toast = Notification(
            app_id="NewsForge",
            title=title,
            msg=message,
            duration="long"
        )
        toast.set_audio(audio.Default, loop=False)
        toast.show()
    except ImportError:
        print(f"🔔 NOTIFICATION: {title} - {message}")
    except Exception as e:
        print(f"Notification error: {e}")


def get_latest_releases():
    """GitHub se latest releases fetch karta hai."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/releases"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"❌ GitHub check error: {e}")
    return []


def download_video(asset_url, filename):
    """Video download karta hai."""
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
    save_path = os.path.join(DOWNLOAD_FOLDER, filename)

    # Already downloaded check
    if os.path.exists(save_path):
        print(f"  ⚠️ Already exists: {filename}")
        return save_path

    print(f"  ⬇️  Downloading: {filename}")

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/octet-stream"
    }

    try:
        response = requests.get(asset_url, headers=headers, stream=True, timeout=300)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))
        downloaded = 0

        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
                f.write(chunk)
                downloaded += len(chunk)
                if total_size:
                    percent = int(downloaded / total_size * 100)
                    print(f"  Progress: {percent}%", end="\r")

        print(f"\n  ✅ Downloaded: {save_path}")
        return save_path

    except Exception as e:
        print(f"  ❌ Download error: {e}")
        if os.path.exists(save_path):
            os.remove(save_path)
        return None


def check_and_download():
    """
    GitHub check karta hai aur naye videos download karta hai.
    """
    seen_releases = load_seen_releases()
    releases = get_latest_releases()

    new_videos = []

    for release in releases:
        release_id = str(release.get("id", ""))

        if release_id in seen_releases:
            continue

        # Naya release mila!
        print(f"\n🆕 Naya video mila: {release.get('name', 'Unknown')}")

        assets = release.get("assets", [])
        for asset in assets:
            if asset.get("name", "").endswith(".mp4"):
                filename = asset["name"]
                download_url = asset["browser_download_url"]

                saved_path = download_video(download_url, filename)

                if saved_path:
                    new_videos.append(saved_path)
                    send_windows_notification(
                        "NewsForge - Naya Video Ready! 🎬",
                        f"Download complete: {filename}\nFolder: {DOWNLOAD_FOLDER}"
                    )

        seen_releases.add(release_id)

    save_seen_releases(seen_releases)

    if new_videos:
        print(f"\n✅ {len(new_videos)} naye video(s) download hue!")
        for v in new_videos:
            print(f"  📁 {v}")
    else:
        print(f"  ℹ️  Koi naya video nahi. [{datetime.now().strftime('%H:%M:%S')}]")


def run_watcher():
    """
    Main watcher loop - continuously check karta hai.
    """
    print("=" * 50)
    print("NewsForge Watcher Started!")
    print(f"Download folder: {DOWNLOAD_FOLDER}")
    print(f"Check interval: {CHECK_INTERVAL // 60} minutes")
    print(f"Repo: {GITHUB_REPO}")
    print("=" * 50)

    # Create download folder
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

    send_windows_notification(
        "NewsForge Watcher Active",
        f"Har {CHECK_INTERVAL//60} minute mein check karunga"
    )

    while True:
        try:
            print(f"\n🔍 Checking... [{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}]")
            check_and_download()
        except KeyboardInterrupt:
            print("\n👋 Watcher band ho raha hai...")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    run_watcher()
