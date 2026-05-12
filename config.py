# ============================================
# NEWSFORGE - CONFIG FILE
# ============================================

# --- API KEYS ---
GROQ_API_KEY = "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"
GITHUB_TOKEN = "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"
GITHUB_REPO = "kundanrana935-cell/news"

# --- CHANNEL SETTINGS ---
CHANNEL_NAME = "Bharat Update"

# --- VIDEO SETTINGS ---
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
VIDEO_FPS = 24
VIDEO_DURATION_TARGET = 570

# --- NEWS SETTINGS ---
NEWS_PER_VIDEO = 6
NEWS_CATEGORIES = [
    "Politics", "Cricket", "Economy", "Technology",
    "Crime", "Bollywood", "Geopolitics", "International", "India"
]

# --- RSS FEEDS ---
RSS_FEEDS = [
    "https://feeds.feedburner.com/ndtvnews-india-news",
    "https://www.aajtak.in/rss/india-news.xml",
    "https://zeenews.india.com/hindi/india/feed",
    "https://www.bbc.com/hindi/india/index.xml",
    "https://www.indiatvnews.com/rss/nation.xml",
    "https://www.abplive.com/topic/india/feed",
    "https://hindi.republicworld.com/feed",
    "https://timesofindia.indiatimes.com/rss.cms",
]

# --- VOICE SETTINGS ---
TTS_VOICE = "hi-IN-SwaraNeural"
TTS_SPEED = "+10%"

# --- IMAGE SETTINGS ---
IMAGE_MIN_WIDTH = 640
IMAGE_MIN_HEIGHT = 480
IMAGE_DURATION = 4
IMAGES_PER_NEWS = 25

# --- AVATAR SETTINGS ---
AVATAR_FILE = "assets/avatar.mp4"
AVATAR_FULL_DURATION = 6
AVATAR_SHORT_DURATION = 3

# --- OUTPUT SETTINGS ---
OUTPUT_DIR = "output"
IMAGES_DIR = "output/images"
AUDIO_DIR = "output/audio"
VIDEOS_DIR = "output/videos"
DATABASE_FILE = "database/newsforge.db"

# --- DOWNLOAD SETTINGS ---
DOWNLOAD_FOLDER = r"C:\NewsVideos"
CHECK_INTERVAL = 300

# --- WEB APP SETTINGS ---
FLASK_PORT = 5000
FLASK_HOST = "localhost"

# --- SCHEDULE SETTINGS ---
START_HOUR = 7
END_HOUR = 22