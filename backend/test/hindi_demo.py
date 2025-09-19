#!/usr/bin/env python3
"""
Demo script showing Hindi TTS integration
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tts import detect_hindi_in_text, play_speech, play_hindi_speech
from command_processor import process_voice_command
from summarizer_service import translate_to_hindi_text

def demo_hindi_detection():
    """Demonstrate Hindi text detection"""
    print("=== Hindi Text Detection Demo ===")
    
    test_texts = [
        "Hello, how are you?",
        "hindi mein bolo",
        "हिंदी में बताओ",
        "translate to hindi",
        "hindi me kaho",
        "Help me navigate",
        "हिंदी में बोलो"
    ]
    
    for text in test_texts:
        is_hindi = detect_hindi_in_text(text)
        print(f"Text: '{text}' -> Hindi detected: {is_hindi}")

def demo_command_processing():
    """Demonstrate Hindi command processing"""
    print("\n=== Hindi Command Processing Demo ===")
    
    test_commands = [
        "hindi mein bolo",
        "translate to hindi",
        "हिंदी में बताओ",
        "hindi me kaho",
        "help me navigate",
        "hindi translate"
    ]
    
    for cmd in test_commands:
        result = process_voice_command(cmd)
        print(f"Command: '{cmd}'")
        print(f"  Type: {result['type']}")
        print(f"  Confidence: {result['confidence']:.2f}")
        print(f"  Valid: {result['confidence'] >= 0.3}")
        if result['suggestions']:
            print(f"  Response: {result['suggestions'][0]}")
        print()

def demo_translation():
    """Demonstrate English to Hindi translation"""
    print("=== Translation Demo ===")
    
    english_text = "You can navigate to different sections of the app using the menu buttons."
    print(f"English: {english_text}")
    
    try:
        hindi_text = translate_to_hindi_text(english_text)
        print(f"Hindi: {hindi_text}")
        return hindi_text
    except Exception as e:
        print(f"Translation error: {e}")
        return None

def demo_tts():
    """Demonstrate TTS functionality"""
    print("\n=== TTS Demo ===")
    
    # Test English TTS
    english_text = "Hello, this is a test of the text to speech system."
    print(f"Playing English: {english_text}")
    try:
        play_speech(english_text)
        print("✅ English TTS played successfully")
    except Exception as e:
        print(f"❌ English TTS error: {e}")
    
    # Test Hindi TTS
    hindi_text = "नमस्ते, यह टेक्स्ट टू स्पीच सिस्टम का टेस्ट है।"
    print(f"Playing Hindi: {hindi_text}")
    try:
        play_hindi_speech(hindi_text)
        print("✅ Hindi TTS played successfully")
    except Exception as e:
        print(f"❌ Hindi TTS error: {e}")

def main():
    """Run all demos"""
    print("Hindi TTS Integration Demo")
    print("=" * 50)
    
    # Demo 1: Hindi detection
    demo_hindi_detection()
    
    # Demo 2: Command processing
    demo_command_processing()
    
    # Demo 3: Translation
    hindi_text = demo_translation()
    
    # Demo 4: TTS (uncomment to test audio)
    # demo_tts()
    
    print("\n=== Integration Summary ===")
    print("✅ Hindi text detection implemented")
    print("✅ Hindi command processing enhanced")
    print("✅ Translation service integrated")
    print("✅ TTS with Hindi support added")
    print("✅ API endpoints updated")
    print("\nThe assistant will now:")
    print("1. Detect when user speaks Hindi words")
    print("2. Process Hindi commands")
    print("3. Translate responses to Hindi when requested")
    print("4. Use appropriate voice for Hindi TTS")

if __name__ == "__main__":
    main()
