#!/usr/bin/env python3
"""
Test script for voice recognition functionality
"""
import os
import sys
import time
from stt import start_realtime_transcription, transcribe

def test_file_transcription():
    """Test transcription of an audio file"""
    print("Testing file transcription...")
    
    # Check if test audio file exists
    test_file = "../whisper/speech.mp3"
    if os.path.exists(test_file):
        print(f"Transcribing file: {test_file}")
        result = transcribe(test_file)
        print(f"Transcription result: '{result}'")
        return result
    else:
        print(f"Test file {test_file} not found")
        return None

def test_realtime_transcription():
    """Test real-time transcription"""
    print("\nTesting real-time transcription...")
    print("Speak into your microphone for 10 seconds...")
    print("Press Ctrl+C to stop early")
    
    try:
        start_realtime_transcription()
    except KeyboardInterrupt:
        print("\nStopped by user")

def main():
    print("Voice Recognition Test")
    print("=" * 30)
    
    # Test file transcription first
    file_result = test_file_transcription()
    
    if file_result and file_result.strip():
        print(f"✅ File transcription working: '{file_result}'")
    else:
        print("❌ File transcription failed or empty result")
    
    # Ask user if they want to test real-time
    print("\nDo you want to test real-time transcription? (y/n): ", end="")
    try:
        response = input().lower().strip()
        if response in ['y', 'yes']:
            test_realtime_transcription()
        else:
            print("Skipping real-time test")
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main()
