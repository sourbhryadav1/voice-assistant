#!/usr/bin/env python3
"""
Test script for Hindi TTS functionality
"""
import requests
import json

def test_hindi_translation():
    """Test Hindi translation functionality"""
    print("Testing Hindi Translation...")
    
    # Test data
    test_data = {
        "text": "You can navigate to different sections of the app using the menu buttons. The home page shows your main dashboard with quick access to features.",
        "translate_to_hindi": True
    }
    
    try:
        response = requests.post(
            'http://127.0.0.1:5000/api/summarize',
            headers={'Content-Type': 'application/json'},
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Translation successful!")
            print(f"Original: {test_data['text']}")
            print(f"Hindi: {data['summary']}")
            print(f"Is Hindi: {data.get('is_hindi', False)}")
            return data['summary']
        else:
            print(f"❌ Translation failed: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_hindi_tts(hindi_text):
    """Test Hindi TTS functionality"""
    if not hindi_text:
        print("No Hindi text to test TTS")
        return
        
    print("\nTesting Hindi TTS...")
    
    # Test regular TTS endpoint
    tts_data = {
        "text": hindi_text,
        "is_hindi": True
    }
    
    try:
        response = requests.post(
            'http://127.0.0.1:5000/api/tts',
            headers={'Content-Type': 'application/json'},
            json=tts_data,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Hindi TTS successful!")
            print(f"Audio size: {len(response.content)} bytes")
            
            # Save the audio file for testing
            with open('hindi_test.mp3', 'wb') as f:
                f.write(response.content)
            print("Audio saved as 'hindi_test.mp3'")
        else:
            print(f"❌ TTS failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_hindi_response_endpoint():
    """Test the new Hindi response endpoint"""
    print("\nTesting Hindi Response Endpoint...")
    
    test_data = {
        "text": "You can navigate to different sections of the app using the menu buttons.",
        "original_text": "You can navigate to different sections of the app using the menu buttons."
    }
    
    try:
        response = requests.post(
            'http://127.0.0.1:5000/api/hindi-response',
            headers={'Content-Type': 'application/json'},
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Hindi Response endpoint successful!")
            print(f"Audio size: {len(response.content)} bytes")
            
            # Save the audio file for testing
            with open('hindi_response_test.mp3', 'wb') as f:
                f.write(response.content)
            print("Audio saved as 'hindi_response_test.mp3'")
        else:
            print(f"❌ Hindi Response failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_command_processor():
    """Test command processor for Hindi commands"""
    print("\nTesting Command Processor...")
    
    from command_processor import process_voice_command
    
    test_commands = [
        "translate to hindi",
        "hindi mein bolo",
        "hindi me translate karo",
        "हिंदी में बताओ",
        "hindi mein batao",
        "hindi me kaho",
        "speak in hindi",
        "talk in hindi",
        "hindi translate",
        "हिंदी में बोलो",
        "help me navigate"
    ]
    
    for cmd in test_commands:
        result = process_voice_command(cmd)
        print(f"Command: '{cmd}'")
        print(f"Type: {result['type']}, Confidence: {result['confidence']:.2f}")
        print(f"Valid: {result['confidence'] >= 0.3}")
        print()

def main():
    print("Hindi TTS Test Suite")
    print("=" * 40)
    
    # Test command processor
    test_command_processor()
    
    # Test translation
    hindi_text = test_hindi_translation()
    
    # Test TTS if translation worked
    if hindi_text:
        test_hindi_tts(hindi_text)
    
    # Test the new Hindi response endpoint
    test_hindi_response_endpoint()
    
    print("\nTest completed!")

if __name__ == "__main__":
    main()
