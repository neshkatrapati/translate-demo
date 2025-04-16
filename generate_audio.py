import os
from pydub import AudioSegment
from google.cloud import texttospeech
import pandas as pd
from datetime import datetime
import sys
import json


language_map = {
    "hi" : {
        "language_code": "hi-IN",
        "name" : "hi-IN-Wavenet-C",
    },
    "in_en" : {
        "language_code": "en-IN",
        "name" : "en-IN-Wavenet-C",
    },
    "te": {
        "language_code": "te-IN",
        "name": "te-IN-Standard-D",
    },
    "kn": {
        "language_code": "kn-IN",
        "name": "kn-IN-Wavenet-C",
    }
}




def timestamp_to_seconds(ts):
    t = datetime.strptime(ts, "%H:%M:%S,%f")
    return t.minute * 60 + t.second + (t.microsecond * 1e-6)

# Load the translated Hindi CSV with correct timestamps
json_path = sys.argv[1]  # Pipe or comma-separated with start_time, end_time, text
target_path = sys.argv[2]
intermediary_path = sys.argv[3]
language = "te"
#prosody = float(sys.argv[5])

if os.path.exists(intermediary_path):
    os.system(f"rm -rf {intermediary_path}")

os.mkdir(intermediary_path)



sentences = json.loads(open(json_path).read())

# Initialize TTS client
client = texttospeech.TextToSpeechClient()

combined = AudioSegment.silent(duration=0)

for idx, text in enumerate(sentences):
    # if idx != 39:
    #     continue


    #continue


    ssml = f"""
    <speak><prosody rate=\"100%\">{text}</prosody></speak>
    """
    #print(ssml)
    synthesis_input = texttospeech.SynthesisInput(ssml=ssml)

    lang_settings = language_map[language]
    voice = texttospeech.VoiceSelectionParams(
        language_code=lang_settings['language_code'],
        name=lang_settings['name'],
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )

    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    clip_path = f"{intermediary_path}/line_{idx:03}.mp3"

    with open(clip_path, "wb") as out:
        out.write(response.audio_content)

    clip = AudioSegment.from_file(clip_path)

    combined += clip

    print(f"[{idx}] Done")


    #print(f"✅ Processed line {idx:03} ({row['start']}–{row['end']}) | Clip: {clip_duration} ms")
    #break
# Export final synced Hindi audio
combined.export(target_path, format="mp3")
print(f"\n🎬 Synced {language} audio saved as '{target_path}'")
