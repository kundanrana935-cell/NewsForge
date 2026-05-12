# ============================================
# WEBAPP - FLASK WEB APP
# Manual mode ke liye
# Browser mein localhost:5000 pe khulega
# ============================================

import os
import sys
import json
import threading
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import FLASK_PORT, FLASK_HOST, CHANNEL_NAME, DOWNLOAD_FOLDER
from database.db import init_database, get_all_videos, save_video_record

app = Flask(__name__)

# Pipeline status track karne ke liye
pipeline_status = {
    "running": False,
    "step": "",
    "progress": 0,
    "message": "",
    "video_path": None,
    "error": None
}


def run_manual_pipeline(script_text, category):
    """
    Background mein manual pipeline run karta hai.
    """
    global pipeline_status

    pipeline_status.update({
        "running": True,
        "step": "starting",
        "progress": 5,
        "message": "Pipeline shuru ho rahi hai...",
        "video_path": None,
        "error": None
    })

    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Step 1: Script clean karo
        pipeline_status.update({"step": "script", "progress": 10, "message": "Script process ho rahi hai..."})
        from modules.script_generator import generate_script_from_manual_text
        clean_script = generate_script_from_manual_text(script_text)

        # Step 2: Keywords extract karo images ke liye
        pipeline_status.update({"step": "keywords", "progress": 20, "message": "Keywords extract ho rahe hain..."})
        words = clean_script.split()
        # Pehle 10 important words = keywords
        keywords = " ".join(words[:15])

        # Fake news item banao image fetcher ke liye
        manual_news_item = {
            "title": keywords[:80],
            "category": category,
            "news_image_url": None,
            "full_content": clean_script[:1000]
        }

        # Step 3: Images fetch karo
        pipeline_status.update({"step": "images", "progress": 30, "message": "Images fetch ho rahi hain (2-3 min)..."})
        from modules.image_fetcher import fetch_all_images_for_news
        images, folder = fetch_all_images_for_news(manual_news_item, f"manual_{timestamp}", target_count=150)
        manual_news_item["images"] = images

        # Step 4: Images process karo
        pipeline_status.update({"step": "processing", "progress": 50, "message": "Images process ho rahi hain..."})
        from modules.image_processor import process_images
        processed_images = process_images(images, f"output/images/manual_{timestamp}_processed")
        manual_news_item["processed_images"] = processed_images

        # Step 5: Voiceover generate karo
        pipeline_status.update({"step": "voice", "progress": 65, "message": "Voiceover generate ho raha hai..."})
        from modules.voiceover import generate_manual_voiceover
        audio_path, audio_duration = generate_manual_voiceover(
            clean_script,
            output_filename=f"manual_{timestamp}_audio.mp3"
        )
        manual_news_item["audio_path"] = audio_path
        manual_news_item["audio_duration"] = audio_duration

        # Step 6: Video build karo
        pipeline_status.update({"step": "video", "progress": 75, "message": "Video ban rahi hai (10-20 min)..."})
        from modules.video_builder import build_full_video
        video_filename = f"manual_video_{timestamp}.mp4"
        video_path, duration = build_full_video([manual_news_item], video_filename)

        if not video_path:
            raise Exception("Video build failed")

        # Step 7: Download folder mein copy karo
        pipeline_status.update({"step": "saving", "progress": 95, "message": "Video save ho rahi hai..."})
        import shutil
        os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
        final_path = os.path.join(DOWNLOAD_FOLDER, video_filename)
        shutil.copy2(video_path, final_path)

        # Database mein save karo
        save_video_record(
            title=keywords[:100],
            category=category,
            mode="manual",
            duration=duration,
            file_path=final_path
        )

        pipeline_status.update({
            "running": False,
            "step": "done",
            "progress": 100,
            "message": f"Video ready! {final_path}",
            "video_path": final_path,
            "error": None
        })

    except Exception as e:
        pipeline_status.update({
            "running": False,
            "step": "error",
            "progress": 0,
            "message": f"Error: {str(e)}",
            "error": str(e)
        })
        print(f"❌ Pipeline error: {e}")


# ==================
# ROUTES
# ==================

@app.route("/")
def home():
    """Home page."""
    return render_template("home.html", channel=CHANNEL_NAME)


@app.route("/manual")
def manual():
    """Manual video creator page."""
    return render_template("manual.html", channel=CHANNEL_NAME)


@app.route("/create_video", methods=["POST"])
def create_video():
    """Video create karna shuru karta hai."""
    global pipeline_status

    if pipeline_status["running"]:
        return jsonify({"error": "Pehle se ek video ban rahi hai. Wait karo."}), 400

    script_text = request.form.get("script", "").strip()
    category = request.form.get("category", "India")

    if len(script_text) < 100:
        return jsonify({"error": "Script bahut chhoti hai. Kam se kam 100 characters likho."}), 400

    # Background mein pipeline run karo
    thread = threading.Thread(
        target=run_manual_pipeline,
        args=(script_text, category),
        daemon=True
    )
    thread.start()

    return jsonify({"success": True, "message": "Video banana shuru ho gaya!"})


@app.route("/status")
def status():
    """Pipeline ka current status return karta hai."""
    return jsonify(pipeline_status)


@app.route("/history")
def history():
    """Video history page."""
    videos = get_all_videos()
    return render_template("history.html", videos=videos, channel=CHANNEL_NAME)


@app.route("/settings")
def settings():
    """Settings page."""
    return render_template("settings.html", channel=CHANNEL_NAME)


if __name__ == "__main__":
    init_database()
    print(f"\n🌐 NewsForge Web App shuru ho raha hai...")
    print(f"   Browser mein kholao: http://{FLASK_HOST}:{FLASK_PORT}")
    print(f"   Band karne ke liye: Ctrl+C\n")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=False)
