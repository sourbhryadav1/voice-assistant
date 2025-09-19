import os
import re
from dotenv import load_dotenv
from openai import OpenAI
import tempfile
from playsound import playsound

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise RuntimeError("OPENAI_API_KEY not in env")

client = OpenAI(api_key=API_KEY)


def detect_hindi_in_text(text: str) -> bool:
    """Detect if text contains Hindi words or characters"""
    if not text:
        return False
    
    # Check for Hindi Unicode range (Devanagari script)
    hindi_pattern = re.compile(r'[\u0900-\u097F]')
    
    # Check for common Hindi words in English (more specific patterns)
    # Removed single-letter words that cause false positives in English
    hindi_words = [
        'hindi', 'hindi mein', 'hindi me', 'hindi mein bolo', 'hindi me bolo',
        'hindi translate', 'hindi me translate', 'hindi mein translate',
        'bolo', 'batao', 'kya', 'kaise', 'kahan', 'kab', 'kyun', 'kisne',
        'main', 'tum', 'aap', 'hum', 'vo', 'ye', 'wo', 'is', 'us',
        'par', 'se', 'ko', 'ka', 'ki', 'ke', 'mein', 'pe', 'tak',
        'hindi me kaho', 'hindi mein kaho', 'hindi me batao', 'hindi mein batao',
        'speak in hindi', 'talk in hindi'
    ]
    
    # Check for Hindi characters
    if hindi_pattern.search(text):
        return True
    
    # Check for Hindi words (case insensitive, word boundaries)
    text_lower = text.lower()
    for word in hindi_words:
        # Use word boundaries to avoid false positives
        if re.search(r'\b' + re.escape(word) + r'\b', text_lower):
            return True
    
    return False


def synthesize_speech(text: str, voice: str = "alloy", model: str = "gpt-4o-mini-tts", out_path: str = "speech.mp3", language: str = "en") -> str:
    if not text or not text.strip():
        raise ValueError("No text provided for TTS")

    # Create speech audio from text and write to file
    speech = client.audio.speech.create(
        model=model,
        voice=voice,
        input=text.strip(),
        response_format="mp3"
    )

    audio_bytes = speech.read()
    with open(out_path, "wb") as f:
        f.write(audio_bytes)

    return os.path.abspath(out_path)


def play_speech(text: str, voice: str = "alloy", model: str = "gpt-4o-mini-tts", language: str = "en") -> None:
    if not text or not text.strip():
        raise ValueError("No text provided for TTS")

    # Detect if text contains Hindi and adjust voice accordingly
    is_hindi = detect_hindi_in_text(text)
    if is_hindi:
        # Use a voice that works better with Hindi (OpenAI TTS supports multiple languages)
        voice = "nova"  # Nova voice works well with Hindi
    
    # Create MP3 bytes, write to a temp file, play, then delete
    speech = client.audio.speech.create(
        model=model,
        voice=voice,
        input=text.strip(),
        response_format="mp3"
    )
    audio_bytes = speech.read()
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    try:
        tmp.write(audio_bytes)
        tmp.flush()
        tmp.close()
        playsound(tmp.name)
    finally:
        try:
            os.remove(tmp.name)
        except OSError:
            pass


def play_hindi_speech(text: str, voice: str = "nova", model: str = "gpt-4o-mini-tts") -> None:
    """Specifically play Hindi text with optimized voice settings"""
    if not text or not text.strip():
        raise ValueError("No text provided for Hindi TTS")

    # Create MP3 bytes, write to a temp file, play, then delete
    speech = client.audio.speech.create(
        model=model,
        voice=voice,
        input=text.strip(),
        response_format="mp3"
    )
    audio_bytes = speech.read()
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    try:
        tmp.write(audio_bytes)
        tmp.flush()
        tmp.close()
        playsound(tmp.name)
    finally:
        try:
            os.remove(tmp.name)
        except OSError:
            pass


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Text-to-Speech using OpenAI TTS")
    parser.add_argument("text", nargs="*", help="Text to speak. If omitted, enters interactive mode.")
    parser.add_argument("--voice", default="alloy", help="TTS voice (default: alloy)")
    parser.add_argument("--model", default="gpt-4o-mini-tts", help="TTS model (default: gpt-4o-mini-tts)")
    parser.add_argument("--out", default=None, help="If provided, save audio to this file; otherwise play")

    args = parser.parse_args()

    try:
        if args.text:
            # Single-shot: use provided text
            text_input = " ".join(args.text)
            if args.out:
                path = synthesize_speech(text_input, voice=args.voice, model=args.model, out_path=args.out)
                print(f"Saved audio to: {path}")
            else:
                play_speech(text_input, voice=args.voice, model=args.model)
        else:
            # Interactive: read line-by-line and speak immediately
            print("Interactive TTS. Type text and press Enter to speak. Empty line to exit.")
            while True:
                try:
                    line = input("> ")
                except EOFError:
                    break
                if not line.strip():
                    break
                play_speech(line, voice=args.voice, model=args.model)
    except Exception as e:
        print(f"TTS error: {e}")
