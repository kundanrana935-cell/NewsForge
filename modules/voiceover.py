# ============================================
# MODULE 6: VOICEOVER
# Edge TTS se Hindi female voice generate karta hai
# Voice: hi-IN-SwaraNeural (same har video mein)
# ============================================

import asyncio
import edge_tts
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TTS_VOICE, TTS_SPEED, AUDIO_DIR


async def _generate_audio(text, output_path, voice, speed):
    """Async audio generation."""
    rate = speed if speed else "+0%"
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(output_path)


def generate_audio(text, filename, voice=TTS_VOICE, speed=TTS_SPEED):
    """
    Text ko audio file mein convert karta hai.
    Returns: audio file path
    """
    os.makedirs(AUDIO_DIR, exist_ok=True)
    output_path = os.path.join(AUDIO_DIR, filename)

    try:
        asyncio.run(_generate_audio(text, output_path, voice, speed))

        if os.path.exists(output_path):
            size_kb = os.path.getsize(output_path) / 1024
            duration = get_audio_duration(output_path)
            print(f"    ✅ Audio: {filename} | {size_kb:.0f}KB | {duration:.1f}s")
            return output_path, duration
        else:
            print(f"    ❌ Audio file nahi bani: {filename}")
            return None, 0

    except Exception as e:
        print(f"    ❌ TTS Error: {e}")
        return None, 0


def get_audio_duration(audio_path):
    """Audio file ki duration seconds mein return karta hai."""
    try:
        from moviepy.editor import AudioFileClip
        clip = AudioFileClip(audio_path)
        duration = clip.duration
        clip.close()
        return duration
    except:
        # Estimate by file size (rough)
        size = os.path.getsize(audio_path)
        return size / 16000  # rough estimate


def generate_all_voiceovers(news_list):
    """
    Sabhi news ke scripts ka voiceover generate karta hai.
    Returns: news_list with audio paths added
    """
    print("\n🎙️  Voiceovers generate ho rahe hain...")
    print(f"  Voice: {TTS_VOICE}")

    for i, news in enumerate(news_list, 1):
        script = news.get("script", "")
        if not script:
            print(f"  ⚠️  News {i}: Script nahi mili, skip kar raha hai")
            news["audio_path"] = None
            news["audio_duration"] = 0
            continue

        print(f"\n  [{i}/{len(news_list)}] {news['title'][:40]}...")
        filename = f"news_{i}_audio.mp3"
        audio_path, duration = generate_audio(script, filename)

        news["audio_path"] = audio_path
        news["audio_duration"] = duration

    return news_list


def generate_manual_voiceover(script, output_filename="manual_video_audio.mp3"):
    """
    Manual mode ke liye voiceover generate karta hai.
    Returns: audio path, duration
    """
    print(f"\n🎙️  Manual script ka voiceover generate ho raha hai...")
    print(f"  Voice: {TTS_VOICE}")
    audio_path, duration = generate_audio(script, output_filename)
    return audio_path, duration


if __name__ == "__main__":
    test_text = "दोस्तों आज की सबसे बड़ी खबर यह है कि भारत में एक नई नीति लागू होने वाली है। यानी कि अब देश में बहुत बड़ा बदलाव आने वाला है।"
    audio_path, duration = generate_audio(test_text, "test_voice.mp3")
    print(f"Test audio: {audio_path}, Duration: {duration:.1f}s")
