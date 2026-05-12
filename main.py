# ============================================
# MAIN.PY - AUTO MODE PIPELINE
# GitHub Actions yahan se sab run karta hai
# ============================================

import os
import sys
import shutil
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db import init_database, mark_news_processed, save_video_record
from modules.trending_detector import get_trending_news
from modules.content_scraper import deep_scrape_news
from modules.image_fetcher import fetch_images_for_all_news
from modules.image_processor import process_all_news_images
from modules.script_generator import generate_all_scripts, save_all_scripts
from modules.voiceover import generate_all_voiceovers
from modules.video_builder import build_full_video
from modules.github_uploader import upload_video
from config import VIDEOS_DIR, NEWS_PER_VIDEO


def cleanup_temp_files():
    """Temp files delete karta hai space bachane ke liye."""
    dirs_to_clean = ["output/images", "output/audio"]
    for d in dirs_to_clean:
        if os.path.exists(d):
            shutil.rmtree(d)
            os.makedirs(d)
    print("🧹 Temp files cleaned!")


def run_auto_pipeline():
    """
    Poora auto pipeline ek baar run karta hai.
    GitHub Actions har 30 minute mein isko call karta hai.
    """
    start_time = datetime.now()
    print("\n" + "=" * 55)
    print(f"🚀 NewsForge Auto Pipeline")
    print(f"   Time: {start_time.strftime('%d %B %Y, %H:%M')}")
    print("=" * 55)

    # Database init
    init_database()

    # STEP 1: Trending news fetch
    print("\n📡 STEP 1: Trending news detect kar raha hai...")
    news_list = get_trending_news()

    if not news_list:
        print("❌ Koi trending news nahi mili. Pipeline band.")
        return False

    # STEP 2: Deep content scrape
    print("\n📄 STEP 2: Articles scrape ho rahe hain...")
    news_list = deep_scrape_news(news_list)

    # STEP 3: Images fetch - charon sources se
    print("\n🖼️  STEP 3: Images fetch ho rahi hain...")
    news_list = fetch_images_for_all_news(news_list)

    # STEP 4: Images process karo
    print("\n🔧 STEP 4: Images process ho rahi hain...")
    news_list = process_all_news_images(news_list)

    # STEP 5: AI scripts generate
    print("\n🤖 STEP 5: AI scripts generate ho rahi hain...")
    news_list = generate_all_scripts(news_list)
    save_all_scripts(news_list)

    # STEP 6: Voiceovers generate
    print("\n🎙️  STEP 6: Voiceovers generate ho rahe hain...")
    news_list = generate_all_voiceovers(news_list)

    # STEP 7: Video build
    print("\n🎬 STEP 7: Final video ban rahi hai...")
    timestamp = start_time.strftime("%Y%m%d_%H%M")
    video_filename = f"news_{timestamp}.mp4"

    result = build_full_video(news_list, video_filename)
    if not result:
        print("❌ Video nahi bani!")
        return False

    video_path, duration = result

    # STEP 8: GitHub pe upload
    print("\n📤 STEP 8: GitHub pe upload ho raha hai...")
    main_title = news_list[0]["title"] if news_list else "News Video"
    download_url = upload_video(video_path, main_title)

    # STEP 9: Database mein save karo
    save_video_record(
        title=main_title,
        category=news_list[0].get("category", "India") if news_list else "India",
        mode="auto",
        duration=duration,
        file_path=video_path,
        github_url=download_url or ""
    )

    # Processed news mark karo
    for news in news_list:
        mark_news_processed(news["link"], news["title"])

    # Cleanup
    cleanup_temp_files()

    # Summary
    end_time = datetime.now()
    total_min = (end_time - start_time).seconds // 60

    print("\n" + "=" * 55)
    print("✅ PIPELINE COMPLETE!")
    print(f"   Total time: {total_min} minutes")
    print(f"   Video: {video_path}")
    print(f"   Duration: {duration/60:.1f} minutes")
    if download_url:
        print(f"   GitHub URL: {download_url}")
    print("=" * 55)
    return True


if __name__ == "__main__":
    success = run_auto_pipeline()
    sys.exit(0 if success else 1)
