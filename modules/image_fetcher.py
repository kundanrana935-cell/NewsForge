# ============================================
# MODULE 3: IMAGE FETCHER
# Charon sources se news related images fetch karta hai
# 1. News website direct
# 2. Google Images (icrawler)
# 3. DuckDuckGo
# 4. Wikipedia Commons
# No API key needed
# ============================================

import os
import sys
import requests
import hashlib
import time
from icrawler.builtin import GoogleImageCrawler
from duckduckgo_search import DDGS
import wikipedia
from urllib.parse import quote
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import IMAGES_DIR, IMAGE_MIN_WIDTH, IMAGE_MIN_HEIGHT

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def make_image_dir(news_index):
    """Har news ke liye alag folder banata hai."""
    folder = os.path.join(IMAGES_DIR, f"news_{news_index}")
    os.makedirs(folder, exist_ok=True)
    return folder


def download_image(url, save_path):
    """Ek image download karta hai."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15, stream=True)
        response.raise_for_status()

        content_type = response.headers.get("content-type", "")
        if "image" not in content_type and not any(
            ext in url.lower() for ext in [".jpg", ".jpeg", ".png", ".webp"]
        ):
            return False

        with open(save_path, "wb") as f:
            for chunk in response.iter_content(8192):
                f.write(chunk)
        return True
    except:
        return False


def get_image_hash(filepath):
    """Image ka MD5 hash nikalta hai duplicate detection ke liye."""
    try:
        with open(filepath, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None


# ==========================================
# SOURCE 1: NEWS WEBSITE DIRECT IMAGE
# ==========================================
def fetch_news_website_image(news_image_url, save_folder, existing_hashes):
    """News article ki direct image download karta hai."""
    images = []
    if not news_image_url:
        return images

    try:
        filename = os.path.join(save_folder, "news_direct_1.jpg")
        if download_image(news_image_url, filename):
            img_hash = get_image_hash(filename)
            if img_hash and img_hash not in existing_hashes:
                existing_hashes.add(img_hash)
                images.append(filename)
                print(f"    ✅ News site image: 1")
    except Exception as e:
        print(f"    ⚠️ News image error: {e}")

    return images


# ==========================================
# SOURCE 2: GOOGLE IMAGES
# ==========================================
def fetch_google_images(keywords, save_folder, count=15):
    """Google Images se images fetch karta hai. No API key."""
    images = []
    try:
        crawler = GoogleImageCrawler(
            storage={"root_dir": save_folder},
            feeder_threads=1,
            parser_threads=1,
            downloader_threads=2
        )
        crawler.crawl(
            keyword=keywords,
            max_num=count,
            filters={
                "size": "medium",
                "type": "photo",
                "license": "noncommercial,modify"
            }
        )

        # Downloaded files list karo
        for f in os.listdir(save_folder):
            if f.startswith("000") and any(f.endswith(ext) for ext in [".jpg", ".jpeg", ".png"]):
                images.append(os.path.join(save_folder, f))

        print(f"    ✅ Google Images: {len(images)}")
    except Exception as e:
        print(f"    ⚠️ Google Images error: {e}")

    return images


# ==========================================
# SOURCE 3: DUCKDUCKGO IMAGES
# ==========================================
def fetch_duckduckgo_images(keywords, save_folder, existing_hashes, count=15):
    """DuckDuckGo se images fetch karta hai. No API key."""
    images = []
    saved = 0

    try:
        with DDGS() as ddgs:
            results = list(ddgs.images(
                keywords,
                region="in-en",
                safesearch="moderate",
                size="Medium",
                max_results=count + 10
            ))

        for i, result in enumerate(results):
            if saved >= count:
                break

            img_url = result.get("image", "")
            if not img_url:
                continue

            filename = os.path.join(save_folder, f"ddg_{i+1}.jpg")
            if download_image(img_url, filename):
                img_hash = get_image_hash(filename)
                if img_hash and img_hash not in existing_hashes:
                    existing_hashes.add(img_hash)
                    images.append(filename)
                    saved += 1
                else:
                    os.remove(filename)

            time.sleep(0.3)

        print(f"    ✅ DuckDuckGo: {saved} images")
    except Exception as e:
        print(f"    ⚠️ DuckDuckGo error: {e}")

    return images


# ==========================================
# SOURCE 4: WIKIPEDIA COMMONS
# ==========================================
def fetch_wikipedia_images(keyword, save_folder, existing_hashes, count=8):
    """Wikipedia se topic related images fetch karta hai."""
    images = []
    saved = 0

    try:
        wikipedia.set_lang("hi")
        search_results = wikipedia.search(keyword, results=3)

        for page_title in search_results[:2]:
            if saved >= count:
                break
            try:
                page = wikipedia.page(page_title, auto_suggest=False)
                for img_url in page.images[:5]:
                    if saved >= count:
                        break
                    if any(ext in img_url.lower() for ext in [".jpg", ".jpeg", ".png"]):
                        if not any(skip in img_url.lower() for skip in ["logo", "icon", "flag", "map"]):
                            filename = os.path.join(save_folder, f"wiki_{saved+1}.jpg")
                            if download_image(img_url, filename):
                                img_hash = get_image_hash(filename)
                                if img_hash and img_hash not in existing_hashes:
                                    existing_hashes.add(img_hash)
                                    images.append(filename)
                                    saved += 1
                                else:
                                    os.remove(filename)
            except:
                continue

        print(f"    ✅ Wikipedia: {saved} images")
    except Exception as e:
        print(f"    ⚠️ Wikipedia error: {e}")

    return images


# ==========================================
# MAIN FUNCTION - SABHI SOURCES COMBINE
# ==========================================
def fetch_all_images_for_news(news_item, news_index, target_count=30):
    """
    Ek news ke liye charon sources se images fetch karta hai.
    Returns: list of image file paths
    """
    title = news_item["title"]
    news_image_url = news_item.get("news_image_url", "")

    print(f"\n  🖼️  Images fetch: {title[:50]}...")

    save_folder = make_image_dir(news_index)
    all_images = []
    existing_hashes = set()

    # Keywords banao
    main_keyword = title[:60]
    # Hindi title se English keywords bhi try karo
    topic_keyword = news_item.get("category", "india news") + " " + title[:30]

    # SOURCE 1: News website direct
    print(f"    📌 Source 1: News website...")
    s1 = fetch_news_website_image(news_image_url, save_folder, existing_hashes)
    all_images.extend(s1)

    # SOURCE 2: Google Images - multiple queries
    print(f"    📌 Source 2: Google Images...")
    google_folder = os.path.join(save_folder, "google")
    os.makedirs(google_folder, exist_ok=True)
    s2 = fetch_google_images(main_keyword, google_folder, count=12)
    # Hash check for google images
    for img in s2:
        h = get_image_hash(img)
        if h and h not in existing_hashes:
            existing_hashes.add(h)
            all_images.append(img)

    # SOURCE 3: DuckDuckGo
    print(f"    📌 Source 3: DuckDuckGo...")
    s3 = fetch_duckduckgo_images(main_keyword, save_folder, existing_hashes, count=12)
    all_images.extend(s3)

    # Agar abhi bhi kam images hain toh aur keywords se try karo
    if len(all_images) < target_count:
        print(f"    📌 Source 3b: DuckDuckGo (topic keyword)...")
        s3b = fetch_duckduckgo_images(topic_keyword, save_folder, existing_hashes, count=8)
        all_images.extend(s3b)

    # SOURCE 4: Wikipedia
    print(f"    📌 Source 4: Wikipedia...")
    wiki_keyword = title.split()[0:4]
    wiki_keyword = " ".join(wiki_keyword)
    s4 = fetch_wikipedia_images(wiki_keyword, save_folder, existing_hashes, count=6)
    all_images.extend(s4)

    print(f"\n    📊 Total images fetched: {len(all_images)}")
    return all_images, save_folder


def fetch_images_for_all_news(news_list):
    """
    Sabhi news items ke liye images fetch karta hai.
    Returns: news_list with images added
    """
    print("\n🖼️  Sabhi news ke liye images fetch ho rahi hain...")

    for i, news in enumerate(news_list, 1):
        images, folder = fetch_all_images_for_news(news, i, target_count=28)
        news["images"] = images
        news["images_folder"] = folder

    return news_list


if __name__ == "__main__":
    test_news = {
        "title": "India Pakistan border tension",
        "category": "Geopolitics",
        "news_image_url": None
    }
    images, folder = fetch_all_images_for_news(test_news, 1)
    print(f"\nTotal: {len(images)} images in {folder}")
