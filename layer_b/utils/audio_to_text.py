import whisper
import tempfile
import os

# 🔴 FORCE FFmpeg path for Whisper (Windows fix)
os.environ["PATH"] += os.pathsep + r"D:\Downloads - Copy-main\ffmpeg-2025-12-24-git-abb1524138-essentials_build\ffmpeg-2025-12-24-git-abb1524138-essentials_build\bin"

# load whisper model once
model = whisper.load_model("base")

def audio_to_text(file):
    # Save uploaded file to temp wav
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp:
        temp.write(file.file.read())
        temp_path = temp.name

    # Transcribe audio
    result = model.transcribe(temp_path)

    # Cleanup temp file
    os.remove(temp_path)

    return result["text"]
