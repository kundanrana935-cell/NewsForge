# ============================================
# MODULE 1: TRENDING DETECTOR
# Google Trends + RSS se trending news detect karta hai
# ============================================

import feedparser
import requests
from bs4 import BeautifulSoup
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import RSS_FEEDS, NEWS_PER_VIDEO, NEWS_CATEGORIES
from database.db import is_news_processed


def get_google_trends_india():
    """Google Trends India se trending topics fetch karta hai. No API key."""
    trending = []
    try:
        url = "https://trends.google.com/trending/rss?geo=IN"
        response = requests.get(url, timeout=10)
        feed = feedparser.parse(response.content)
        for entry in feed.entries:
            trending.append(entry.title.lower())
        print(f"  ✅ Google Trends: {len(trending)} trending topics mile")
    except Exception as e:
        print(f"  ⚠️ Google Trends error: {e}")
    return trending


def fetch_all_rss_news():
    """Sabhi RSS feeds se news fetch karta hai."""
    all_news = []
    print("\n📡 RSS feeds se news fetch ho rahi hai...")

    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            source = feed.feed.get("title", "Unknown")
            count = 0
            for entry in feed.entries[:10]:
                title = entry.get("title", "").strip()
                summary = entry.get("summary", entry.get("description", "")).strip()
                link = entry.get("link", "").strip()
                published = entry.get("published", "")

                if not title or not link:
                    continue

                # Already processed check
                if is_news_processed(link):
                    continue

                # HTML tags summary se remove karo
                if summary:
                    soup = BeautifulSoup(summary, "html.parser")
                    summary = soup.get_text()

                all_news.append({
                    "title": title,
                    "summary": summary[:500],
                    "link": link,
                    "source": source,
                    "published": published,
                    "trending_score": 0
                })
                count += 1

            print(f"  ✅ {source}: {count} new news")
        except Exception as e:
            print(f"  ❌ Error {feed_url}: {e}")

    print(f"\n📰 Total unique news: {len(all_news)}")
    return all_news


def score_news_by_trending(news_list, trending_topics):
    """
    News ko trending topics ke saath match karke score deta hai.
    Zyada score = zyada trending.
    """
    for news in news_list:
        score = 0
        title_lower = news["title"].lower()

        for trend in trending_topics:
            trend_words = trend.split()
            for word in trend_words:
                if len(word) > 3 and word in title_lower:
                    score += 1

        news["trending_score"] = score

    # Score ke hisaab se sort karo
    news_list.sort(key=lambda x: x["trending_score"], reverse=True)
    return news_list


def detect_category(title):
    """News ki category automatically detect karta hai."""
    title_lower = title.lower()

    category_keywords = {
        "Cricket": ["cricket", "ipl", "bcci", "virat", "rohit", "test match", "odi", "t20"],
        "Bollywood": ["bollywood", "film", "movie", "actor", "actress", "shahrukh", "salman", "deepika"],
        "Politics": ["modi", "bjp", "congress", "election", "parliament", "minister", "government", "party"],
        "Economy": ["economy", "gdp", "budget", "market", "sensex", "nifty", "rupee", "inflation", "rbi"],
        "Technology": ["technology", "tech", "ai", "artificial intelligence", "startup", "app", "smartphone"],
        "Crime": ["crime", "murder", "arrest", "police", "court", "verdict", "criminal", "rape", "scam"],
        "Geopolitics": ["china", "pakistan", "russia", "usa", "america", "war", "missile", "nato", "border"],
        "International": ["world", "global", "international", "united nations", "un ", "eu ", "europe"],
    }

    for category, keywords in category_keywords.items():
        for kw in keywords:
            if kw in title_lower:
                return category

    return "India"


def get_trending_news():
    """
    Main function - trending news select karke return karta hai.
    Returns: list of selected news items for video
    """
    print("\n🔍 Trending news detect kar raha hai...")

    # Step 1: Trending topics fetch karo
    trending_topics = get_google_trends_india()

    # Step 2: RSS se saari news fetch karo
    all_news = fetch_all_rss_news()

    if not all_news:
        print("❌ Koi news nahi mili!")
        return []

    # Step 3: Trending score assign karo
    scored_news = score_news_by_trending(all_news, trending_topics)

    # Step 4: Category assign karo
    for news in scored_news:
        news["category"] = detect_category(news["title"])

    # Step 5: Top NEWS_PER_VIDEO news select karo
    selected = scored_news[:NEWS_PER_VIDEO]

    print(f"\n✅ {len(selected)} news selected for video:")
    for i, news in enumerate(selected, 1):
        print(f"  {i}. [{news['category']}] {news['title'][:60]}... (score: {news['trending_score']})")

    return selected


if __name__ == "__main__":
    news = get_trending_news()
