# ============================================
# MODULE 7: VIDEO BUILDER
# Avatar + Images (Ken Burns) + Voice = Final Video
# No text overlays, no ticker, no thumbnail
# Clean professional news video
# ============================================

import os
import sys
import random
import numpy as np
from moviepy.editor import (
    VideoFileClip, AudioFileClip, ImageClip,
    concatenate_videoclips, CompositeVideoClip,
    ColorClip, vfx
)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS,
    AVATAR_FILE, AVATAR_FULL_DURATION, AVATAR_SHORT_DURATION,
    VIDEOS_DIR, IMAGE_DURATION
)


def load_avatar_clip(duration=None):
    """
    Avatar clip load karta hai aur required duration tak trim/loop karta hai.
    """
    if not os.path.exists(AVATAR_FILE):
        print(f"  ⚠️ Avatar file nahi mili: {AVATAR_FILE}")
        return None

    try:
        avatar = VideoFileClip(AVATAR_FILE)
        avatar_duration = avatar.duration

        if duration is None:
            duration = AVATAR_FULL_DURATION

        # Avatar ko required duration tak trim ya loop karo
        if avatar_duration >= duration:
            # Trim karo
            clip = avatar.subclip(0, duration)
        else:
            # Loop karo
            loops_needed = int(duration / avatar_duration) + 1
            clips = [avatar] * loops_needed
            clip = concatenate_videoclips(clips).subclip(0, duration)

        # Resize karo video size ke hisaab se
        clip = clip.resize((VIDEO_WIDTH, VIDEO_HEIGHT))
        return clip

    except Exception as e:
        print(f"  ❌ Avatar load error: {e}")
        return None


def apply_ken_burns_effect(image_path, duration=IMAGE_DURATION, effect=None):
    """
    Ek image pe Ken Burns effect apply karta hai.
    Effects: zoom_in, zoom_out, pan_left, pan_right
    Returns: moviepy clip
    """
    if effect is None:
        effects = ["zoom_in", "zoom_out", "pan_left", "pan_right"]
        effect = random.choice(effects)

    try:
        img_clip = ImageClip(image_path).set_duration(duration)

        if effect == "zoom_in":
            # 100% se 120% tak zoom in
            def zoom_in_effect(t):
                scale = 1.0 + 0.2 * (t / duration)
                return scale
            clip = img_clip.resize(lambda t: zoom_in_effect(t))

        elif effect == "zoom_out":
            # 120% se 100% tak zoom out
            def zoom_out_effect(t):
                scale = 1.2 - 0.2 * (t / duration)
                return scale
            clip = img_clip.resize(lambda t: zoom_out_effect(t))

        elif effect == "pan_left":
            # Left se right pan
            clip = img_clip.resize(1.15)  # Thoda bada karo pan ke liye
            w_diff = clip.w - VIDEO_WIDTH
            clip = clip.set_position(lambda t: (-int(w_diff * t / duration), 0))
            clip = clip.crop(x1=0, y1=0, width=VIDEO_WIDTH, height=VIDEO_HEIGHT)

        elif effect == "pan_right":
            # Right se left pan
            clip = img_clip.resize(1.15)
            w_diff = clip.w - VIDEO_WIDTH
            clip = clip.set_position(lambda t: (-int(w_diff * (1 - t / duration)), 0))
            clip = clip.crop(x1=0, y1=0, width=VIDEO_WIDTH, height=VIDEO_HEIGHT)

        else:
            clip = img_clip

        return clip.resize((VIDEO_WIDTH, VIDEO_HEIGHT))

    except Exception as e:
        print(f"    ⚠️ Ken Burns error ({effect}): {e}")
        # Fallback - simple static image
        try:
            return ImageClip(image_path).set_duration(duration).resize((VIDEO_WIDTH, VIDEO_HEIGHT))
        except:
            return ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=(20, 20, 50), duration=duration)


def create_image_slideshow(image_paths, total_duration, crossfade=0.5):
    """
    Images ki slideshow banata hai Ken Burns effect ke saath.
    Returns: video clip
    """
    if not image_paths:
        return ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=(20, 20, 50), duration=total_duration)

    # Calculate images needed
    effective_duration = IMAGE_DURATION - crossfade
    images_needed = max(int(total_duration / effective_duration) + 2, len(image_paths))

    # Agar kam images hain toh loop karo
    looped_images = []
    while len(looped_images) < images_needed:
        looped_images.extend(image_paths)
    looped_images = looped_images[:images_needed]

    # Effects assign karo - consecutive same nahi hona chahiye
    effects = ["zoom_in", "zoom_out", "pan_left", "pan_right"]
    random.shuffle(effects)

    clips = []
    for i, img_path in enumerate(looped_images):
        effect = effects[i % len(effects)]
        clip = apply_ken_burns_effect(img_path, IMAGE_DURATION, effect)
        clips.append(clip)

    # Crossfade transitions ke saath join karo
    if len(clips) == 1:
        final = clips[0].subclip(0, min(total_duration, clips[0].duration))
    else:
        # Manual crossfade
        final_clips = [clips[0]]
        for i in range(1, len(clips)):
            clip_with_fade = clips[i].crossfadein(crossfade)
            final_clips.append(clip_with_fade)

        final = concatenate_videoclips(final_clips, padding=-crossfade, method="compose")

    # Exact duration pe trim karo
    if final.duration > total_duration:
        final = final.subclip(0, total_duration)

    return final


def build_news_segment(news_item, segment_index):
    """
    Ek news segment ke liye video banata hai.
    Avatar (short) + Images slideshow + Audio
    Returns: video clip
    """
    audio_path = news_item.get("audio_path")
    images = news_item.get("processed_images", [])

    if not audio_path or not os.path.exists(audio_path):
        print(f"  ❌ News {segment_index}: Audio nahi mili")
        return None

    print(f"\n  🎬 News {segment_index} segment build ho raha hai...")

    # Audio load karo
    audio_clip = AudioFileClip(audio_path)
    audio_duration = audio_clip.duration

    clips_to_join = []

    # Avatar clip (short - segment ke shuru mein)
    avatar_short = load_avatar_clip(duration=AVATAR_SHORT_DURATION)
    if avatar_short:
        # Avatar ke saath koi audio nahi - seedha news audio shuru hoga
        clips_to_join.append(avatar_short.set_audio(None))
        print(f"    ✅ Avatar: {AVATAR_SHORT_DURATION}s added")

    # Images slideshow with audio
    print(f"    🖼️  Slideshow: {len(images)} images, {audio_duration:.1f}s duration")
    slideshow = create_image_slideshow(images, audio_duration)
    slideshow_with_audio = slideshow.set_audio(audio_clip)
    clips_to_join.append(slideshow_with_audio)

    # Sab join karo
    if len(clips_to_join) == 1:
        segment = clips_to_join[0]
    else:
        segment = concatenate_videoclips(clips_to_join, method="compose")

    print(f"    ✅ Segment {segment_index} ready: {segment.duration:.1f}s")
    return segment


def build_full_video(news_list, output_filename):
    """
    Sabhi segments se final video banata hai.
    
    Structure:
    Avatar (full) -> News 1 -> News 2 -> ... -> News N -> Avatar (full)
    """
    os.makedirs(VIDEOS_DIR, exist_ok=True)
    output_path = os.path.join(VIDEOS_DIR, output_filename)

    print("\n🎬 Full video assembly shuru ho rahi hai...")

    all_segments = []

    # Opening avatar (full duration)
    print("\n  📌 Opening avatar add kar raha hai...")
    opening_avatar = load_avatar_clip(duration=AVATAR_FULL_DURATION)
    if opening_avatar:
        all_segments.append(opening_avatar.set_audio(None))
        print(f"    ✅ Opening avatar: {AVATAR_FULL_DURATION}s")
    else:
        # Avatar nahi hai toh black screen
        black = ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=(0, 0, 0), duration=2)
        all_segments.append(black)

    # Har news segment
    for i, news in enumerate(news_list, 1):
        print(f"\n  📌 News {i}/{len(news_list)}: {news['title'][:40]}...")
        segment = build_news_segment(news, i)
        if segment:
            all_segments.append(segment)
        else:
            print(f"    ⚠️ News {i} skip kiya")

    # Closing avatar (full duration)
    print("\n  📌 Closing avatar add kar raha hai...")
    closing_avatar = load_avatar_clip(duration=AVATAR_FULL_DURATION)
    if closing_avatar:
        all_segments.append(closing_avatar.set_audio(None))
        print(f"    ✅ Closing avatar: {AVATAR_FULL_DURATION}s")

    if not all_segments:
        print("❌ Koi bhi segment ready nahi hua!")
        return None

    # Sab segments join karo
    print(f"\n  🔗 {len(all_segments)} segments join ho rahe hain...")
    final_video = concatenate_videoclips(all_segments, method="compose")

    total_duration = final_video.duration
    print(f"  ⏱️  Total video duration: {total_duration:.1f}s ({total_duration/60:.1f} min)")

    # Export karo
    print(f"\n  💾 Video export ho raha hai: {output_path}")
    print("  ⏳ Yeh 10-20 minute le sakta hai...")

    final_video.write_videofile(
        output_path,
        fps=VIDEO_FPS,
        codec="libx264",
        audio_codec="aac",
        bitrate="4000k",
        audio_bitrate="192k",
        temp_audiofile="output/temp_audio.m4a",
        remove_temp=True,
        verbose=False,
        logger=None,
        threads=4
    )

    print(f"\n✅ Video ready: {output_path}")
    print(f"   Size: {os.path.getsize(output_path) / (1024*1024):.1f} MB")
    print(f"   Duration: {total_duration/60:.1f} minutes")

    return output_path, total_duration


if __name__ == "__main__":
    print("Video Builder module ready!")
    print(f"Resolution: {VIDEO_WIDTH}x{VIDEO_HEIGHT} @ {VIDEO_FPS}fps")
