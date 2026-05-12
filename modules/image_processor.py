# ============================================
# MODULE 4: IMAGE PROCESSOR
# Images filter, resize, quality check karta hai
# ============================================

import os
import sys
import cv2
import numpy as np
from PIL import Image
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import VIDEO_WIDTH, VIDEO_HEIGHT, IMAGE_MIN_WIDTH, IMAGE_MIN_HEIGHT


def check_image_valid(filepath):
    """Image valid aur good quality hai check karta hai."""
    try:
        # PIL se open karo
        img = Image.open(filepath)
        width, height = img.size

        # Size check
        if width < IMAGE_MIN_WIDTH or height < IMAGE_MIN_HEIGHT:
            return False, "too_small"

        # Corrupt check
        img.verify()
        return True, "ok"

    except Exception:
        return False, "corrupt"


def check_image_blur(filepath):
    """Image blurry toh nahi hai check karta hai."""
    try:
        img = cv2.imread(filepath)
        if img is None:
            return True  # Unreadable = reject

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

        # 50 se kam = blurry
        return laplacian_var < 50
    except:
        return True


def resize_to_landscape(filepath, output_path):
    """
    Image ko 1920x1080 pe resize karta hai.
    Portrait images crop karke landscape banata hai.
    """
    try:
        img = Image.open(filepath).convert("RGB")
        orig_w, orig_h = img.size

        target_ratio = VIDEO_WIDTH / VIDEO_HEIGHT  # 16:9
        orig_ratio = orig_w / orig_h

        if orig_ratio < target_ratio:
            # Portrait ya square - crop karke landscape banao
            new_height = int(orig_w / target_ratio)
            top = (orig_h - new_height) // 2
            img = img.crop((0, top, orig_w, top + new_height))
        
        # Final resize
        img = img.resize((VIDEO_WIDTH, VIDEO_HEIGHT), Image.LANCZOS)
        img.save(output_path, "JPEG", quality=90)
        return True

    except Exception as e:
        return False


def process_images(image_paths, output_folder):
    """
    Images ko filter, quality check aur resize karta hai.
    Returns: list of processed image paths (ready for video)
    """
    os.makedirs(output_folder, exist_ok=True)
    processed = []
    rejected = 0

    print(f"\n🔧 {len(image_paths)} images process ho rahi hain...")

    for i, img_path in enumerate(image_paths):
        if not os.path.exists(img_path):
            continue

        # Valid check
        valid, reason = check_image_valid(img_path)
        if not valid:
            rejected += 1
            continue

        # Blur check
        if check_image_blur(img_path):
            rejected += 1
            continue

        # Resize to 1920x1080
        output_path = os.path.join(output_folder, f"processed_{i+1:03d}.jpg")
        if resize_to_landscape(img_path, output_path):
            processed.append(output_path)

    print(f"  ✅ Processed: {len(processed)} images")
    print(f"  ❌ Rejected: {rejected} images")
    return processed


def process_all_news_images(news_list):
    """
    Sabhi news ke images process karta hai.
    """
    from config import IMAGES_DIR

    for i, news in enumerate(news_list, 1):
        raw_images = news.get("images", [])
        if not raw_images:
            news["processed_images"] = []
            continue

        output_folder = os.path.join(IMAGES_DIR, f"news_{i}_processed")
        processed = process_images(raw_images, output_folder)
        news["processed_images"] = processed
        print(f"  News {i}: {len(processed)} images ready")

    return news_list


if __name__ == "__main__":
    print("Image Processor ready!")
