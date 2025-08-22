import base64
from openai import OpenAI
import os

from news_forecaster import AudioScript, GenerateAudio, dummy_script


if __name__ == "__main__":
    TODAY = "2025:08:21-14:08:30"
    BASE = f"/Users/zachwolpe/Documents/build/younews/Engine/reports/{TODAY}"
    markdown_file = f"{BASE}/news-report.md"
    title_file = f"{BASE}/main_title.txt"
    save_audio_file = f"{BASE}/audio.wav"
    save_script_file = f"{BASE}/audio_script.txt"
    with open(title_file, "r") as f:
        title = f.read()

    with open(markdown_file, "r") as f:
        markdown_text = f.read()

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # generate script
    script = AudioScript.generate_audio_script(client, title, markdown_text)    
    script = dummy_script()
    AudioScript.save_script(script, save_script_file)
    print(f"> Saved audio script to {save_script_file}")

    audio_generator = GenerateAudio(client)
    audio_generator.generate_audio(script, save_audio_file)
    print(f"> Saved audio to {save_audio_file}")
