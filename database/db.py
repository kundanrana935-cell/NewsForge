# ============================================
# DATABASE MODULE
# SQLite database setup aur operations
# ============================================

import sqlite3
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATABASE_FILE


def init_database():
    """Database aur tables create karta hai."""
    os.makedirs(os.path.dirname(DATABASE_FILE), exist_ok=True)
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # Videos table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT,
            mode TEXT DEFAULT 'auto',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            duration REAL,
            file_path TEXT,
            github_url TEXT,
            youtube_uploaded INTEGER DEFAULT 0
        )
    ''')

    # Processed news table - same news dobara na bane
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS processed_news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            news_url TEXT UNIQUE,
            news_title TEXT,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Database ready!")


def is_news_processed(url):
    """Check karta hai ki yeh news pehle process ho chuki hai."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM processed_news WHERE news_url = ?", (url,))
    result = cursor.fetchone()
    conn.close()
    return result is not None


def mark_news_processed(url, title):
    """News ko processed mark karta hai."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO processed_news (news_url, news_title) VALUES (?, ?)",
            (url, title)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()


def save_video_record(title, category, mode, duration, file_path, github_url=""):
    """Video record database mein save karta hai."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO videos (title, category, mode, duration, file_path, github_url)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (title, category, mode, duration, file_path, github_url))
    conn.commit()
    video_id = cursor.lastrowid
    conn.close()
    return video_id


def get_all_videos():
    """Saari videos ki list return karta hai."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM videos ORDER BY created_at DESC")
    videos = cursor.fetchall()
    conn.close()
    return videos


def mark_youtube_uploaded(video_id):
    """Video ko YouTube uploaded mark karta hai."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE videos SET youtube_uploaded = 1 WHERE id = ?",
        (video_id,)
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_database()
