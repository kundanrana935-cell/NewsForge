# ============================================
# MODULE 5: SCRIPT GENERATOR
# Groq AI se Hindi script banata hai
# Bilkul usi style mein jo user ne example mein bheja
# ============================================

import requests
import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GROQ_API_KEY, CHANNEL_NAME


GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"


def build_prompt(news_item):
    """Ek news ke liye Groq prompt banata hai."""

    title = news_item["title"]
    content = news_item.get("full_content", news_item.get("summary", ""))
    source = news_item.get("source", "news agency")
    category = news_item.get("category", "India")

    prompt = f"""Tum ek experienced Hindi news anchor ho jo YouTube pe news analysis karta hai. Neeche di gayi khabar ke liye ek detailed Hindi script likho.

KHABAR KI JANKARI:
Headline: {title}
Category: {category}
Source: {source}
Content: {content[:3000]}

SCRIPT LIKHNE KE RULES - INHE BILKUL FOLLOW KARO:

1. Script seedha khabar se shuru karo. Koi "Namaskar", "Hello", "Intro" mat likho. Ekdum pehle word se khabar shuru ho.

2. Tone bilkul aise ho:
   - "दोस्तों [headline se seedha shuru]..."
   - Dramatic aur urgent feeling
   - Jaise koi dost bahut important baat bata raha ho

3. Yeh connecting phrases zaroor use karo:
   - "यानी कि" - explanation ke liye
   - "इस वजह से" - cause-effect ke liye  
   - "लेकिन" - contrast ke liye
   - "अब" - situation update ke liye
   - "सिर्फ और सिर्फ" - emphasis ke liye
   - "जाहिर सी बात है" - logical conclusion ke liye

4. News agency ka reference do: "[agency name] के हवाले से बताया गया है..."

5. Rhetorical questions zaroor daalo: "लेकिन सवाल यह है कि...?", "अब क्या होगा...?"

6. Deep analysis karo - sirf facts mat batao, unka matlab samjhao, impact batao

7. Script 900 se 1100 words ki honi chahiye

8. End mein channel ka naam lo: "फिलहाल के लिए {CHANNEL_NAME} के साथ इस खबर में इतना ही। आप देखते रहिए {CHANNEL_NAME}।"

9. Koi heading mat likho, koi [SEGMENT] tags mat likho. Sirf plain flowing text.

10. Bilkul Hindi mein likho. English words sirf tab jab Hindi alternative nahi ho (jaise "bill", "legal").

EXAMPLE STYLE (isi tarah likho):
"दोस्तों होरमज़ में आईआरजीसी के कंट्रोल को अब कानूनी हक मिलने वाला है। ईरान की ताकत अब और मजबूत हो गई है... यानी कि ईरान की पार्लियामेंट में होरमुस में लीगल राइट्स के लिए बकायदा बिल तैयार कर लिया गया है... इस वजह से अमेरिका के लिए मुश्किलें और ज्यादा बढ़ गई हैं..."

Ab script likho:"""

    return prompt


def generate_script_for_news(news_item):
    """
    Groq AI se ek news ke liye script generate karta hai.
    Returns: script string
    """
    prompt = build_prompt(news_item)

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.75,
        "max_tokens": 2000
    }

    try:
        response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        script = data["choices"][0]["message"]["content"].strip()
        print(f"    ✅ Script generated: {len(script.split())} words")
        return script

    except Exception as e:
        print(f"    ❌ Groq error: {e}")
        return generate_fallback_script(news_item)


def generate_fallback_script(news_item):
    """Agar Groq fail ho toh basic script banata hai."""
    title = news_item["title"]
    content = news_item.get("full_content", news_item.get("summary", ""))
    source = news_item.get("source", "न्यूज़ एजेंसी")

    script = f"""दोस्तों {title}। यह एक बहुत ही महत्वपूर्ण खबर है जिसके बारे में आज हम आपको विस्तार से बताने वाले हैं।

{source} के हवाले से बताया गया है कि {content[:500]}

यानी कि यह स्थिति बहुत ही गंभीर है और इसके दूरगामी परिणाम हो सकते हैं। इस वजह से सभी की नजरें इस खबर पर टिकी हुई हैं।

लेकिन सवाल यह है कि आगे क्या होगा? अब जो भी फैसला होगा वह सिर्फ और सिर्फ इस मुद्दे पर निर्भर करेगा। जाहिर सी बात है कि यह मामला अभी और आगे बढ़ेगा।

फिलहाल के लिए {CHANNEL_NAME} के साथ इस खबर में इतना ही। आप देखते रहिए {CHANNEL_NAME}।"""

    return script


def generate_all_scripts(news_list):
    """
    Sabhi news ke liye scripts generate karta hai.
    Returns: news_list with scripts added
    """
    print("\n🤖 AI scripts generate ho rahi hain...")

    for i, news in enumerate(news_list, 1):
        print(f"\n  [{i}/{len(news_list)}] {news['title'][:50]}...")
        script = generate_script_for_news(news)
        news["script"] = script

    return news_list


def generate_script_from_manual_text(manual_script):
    """
    Manual mode ke liye - user ka script as-is return karta hai.
    Koi AI processing nahi, sirf clean karo.
    """
    # Basic cleanup
    script = manual_script.strip()
    # Multiple spaces remove karo
    import re
    script = re.sub(r'\s+', ' ', script)
    return script


def save_all_scripts(news_list, output_dir="output"):
    """Scripts ko text files mein save karta hai."""
    os.makedirs(output_dir, exist_ok=True)
    for i, news in enumerate(news_list, 1):
        script = news.get("script", "")
        if script:
            filepath = os.path.join(output_dir, f"script_news_{i}.txt")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(news["title"] + "\n\n")
                f.write(script)
            print(f"  📄 Script saved: {filepath}")


if __name__ == "__main__":
    test_news = {
        "title": "भारत ने पाकिस्तान के साथ सीमा पर नई सैन्य तैनाती की",
        "category": "Geopolitics",
        "source": "NDTV",
        "summary": "भारत ने पाकिस्तान की सीमा पर अतिरिक्त सैनिक तैनात किए हैं।",
        "full_content": "भारत ने पाकिस्तान की सीमा पर अतिरिक्त सैनिक तैनात किए हैं। यह कदम हाल की घटनाओं के बाद उठाया गया है।"
    }
    script = generate_script_for_news(test_news)
    print("\n--- GENERATED SCRIPT ---")
    print(script[:500])
