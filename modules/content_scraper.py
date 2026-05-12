# ============================================
# MODULE 2: CONTENT SCRAPER
# News article ka poora content scrape karta hai
# Script ke liye deep content chahiye
# ============================================

import requests
from bs4 import BeautifulSoup
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def scrape_article(url):
    """
    Kisi bhi news article ka poora text scrape karta hai.
    Returns: full article text
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")

        # Unwanted elements remove karo
        for tag in soup(["script", "style", "nav", "footer", "header",
                         "aside", "advertisement", "iframe", "form"]):
            tag.decompose()

        # Article content dhundho - common tags
        content = ""
        article_tags = soup.find_all([
            "article", "div", "section", "main"
        ], class_=lambda x: x and any(
            word in str(x).lower() for word in
            ["article", "content", "story", "body", "text", "news-detail", "post-content"]
        ))

        if article_tags:
            for tag in article_tags[:3]:
                text = tag.get_text(separator=" ", strip=True)
                if len(text) > len(content):
                    content = text

        # Agar specific tags nahi mile toh p tags se content lo
        if len(content) < 200:
            paragraphs = soup.find_all("p")
            content = " ".join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50])

        # Clean karo
        content = " ".join(content.split())
        return content[:5000]  # Max 5000 chars

    except Exception as e:
        print(f"    ⚠️ Scrape error {url}: {e}")
        return ""


def scrape_news_image(url):
    """
    News article se main image URL fetch karta hai.
    Returns: image url ya None
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.content, "lxml")

        # OG image sabse reliable hai
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            return og_image["content"]

        # Twitter card image
        twitter_image = soup.find("meta", attrs={"name": "twitter:image"})
        if twitter_image and twitter_image.get("content"):
            return twitter_image["content"]

        # Article ke andar pehli badi image
        images = soup.find_all("img")
        for img in images:
            src = img.get("src", "")
            if src and any(ext in src.lower() for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                if not any(skip in src.lower() for skip in ["logo", "icon", "avatar", "ad"]):
                    return src

    except Exception as e:
        print(f"    ⚠️ Image fetch error: {e}")

    return None


def deep_scrape_news(news_list):
    """
    Har news ke liye deep content scrape karta hai.
    Returns: news list with full content added
    """
    print("\n📄 Articles ka deep content scrape ho raha hai...")

    for i, news in enumerate(news_list, 1):
        print(f"  [{i}/{len(news_list)}] {news['title'][:50]}...")

        # Main article scrape karo
        full_content = scrape_article(news["link"])

        # News site image bhi fetch karo
        news_image_url = scrape_news_image(news["link"])

        # Summary + full content combine karo
        if full_content:
            news["full_content"] = news["summary"] + " " + full_content
        else:
            news["full_content"] = news["summary"]

        news["news_image_url"] = news_image_url

        print(f"    ✅ Content: {len(news['full_content'])} chars, Image: {'Yes' if news_image_url else 'No'}")

        # Server pe load mat daalo
        time.sleep(1)

    return news_list


if __name__ == "__main__":
    test_url = "https://www.ndtv.com/india-news"
    print(f"Testing scraper on: {test_url}")
    content = scrape_article(test_url)
    print(f"Content length: {len(content)}")
    print(content[:300])
