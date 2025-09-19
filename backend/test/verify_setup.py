#!/usr/bin/env python3
"""
Verification script to test all components of the Hindi TTS integration
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all module imports"""
    print("🔍 Testing module imports...")
    
    try:
        from tts import detect_hindi_in_text, play_speech, play_hindi_speech
        print("✅ TTS module imported successfully")
    except Exception as e:
        print(f"❌ TTS module import failed: {e}")
        return False
    
    try:
        from command_processor import process_voice_command, is_valid_voice_command
        print("✅ Command processor imported successfully")
    except Exception as e:
        print(f"❌ Command processor import failed: {e}")
        return False
    
    try:
        from summarizer_service import summarize, translate_to_hindi_text
        print("✅ Summarizer service imported successfully")
    except Exception as e:
        print(f"❌ Summarizer service import failed: {e}")
        return False
    
    try:
        from main import app
        print("✅ Flask app imported successfully")
    except Exception as e:
        print(f"❌ Flask app import failed: {e}")
        return False
    
    return True

def test_hindi_detection():
    """Test Hindi text detection"""
    print("\n🔍 Testing Hindi text detection...")
    
    from tts import detect_hindi_in_text
    
    test_cases = [
        ("Hello world", False),
        ("hindi mein bolo", True),
        ("हिंदी में बताओ", True),
        ("translate to hindi", True),
        ("hindi me kaho", True),
        ("Help me navigate", False)
    ]
    
    all_passed = True
    for text, expected in test_cases:
        result = detect_hindi_in_text(text)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{text}' -> {result} (expected: {expected})")
        if result != expected:
            all_passed = False
    
    return all_passed

def test_command_processing():
    """Test voice command processing"""
    print("\n🔍 Testing command processing...")
    
    from command_processor import process_voice_command
    
    test_commands = [
        "hindi mein bolo",
        "translate to hindi",
        "हिंदी में बताओ",
        "help me navigate",
        "hindi me kaho"
    ]
    
    all_passed = True
    for cmd in test_commands:
        result = process_voice_command(cmd)
        is_hindi_cmd = result['type'] == 'hindi'
        confidence = result['confidence']
        
        # Check if Hindi commands are detected correctly
        if 'hindi' in cmd.lower() or 'हिंदी' in cmd:
            expected_hindi = True
        else:
            expected_hindi = False
        
        status = "✅" if is_hindi_cmd == expected_hindi and confidence >= 0.3 else "❌"
        print(f"{status} '{cmd}' -> Type: {result['type']}, Confidence: {confidence:.2f}")
        
        if not (is_hindi_cmd == expected_hindi and confidence >= 0.3):
            all_passed = False
    
    return all_passed

def test_translation():
    """Test translation functionality"""
    print("\n🔍 Testing translation...")
    
    try:
        from summarizer_service import translate_to_hindi_text
        
        english_text = "Hello, how are you?"
        hindi_text = translate_to_hindi_text(english_text)
        
        if hindi_text and hindi_text != english_text:
            print(f"✅ Translation successful")
            print(f"   English: {english_text}")
            print(f"   Hindi: {hindi_text}")
            return True
        else:
            print("❌ Translation failed or returned same text")
            return False
            
    except Exception as e:
        print(f"❌ Translation test failed: {e}")
        return False

def test_environment():
    """Test environment variables"""
    print("\n🔍 Testing environment variables...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    openai_key = os.getenv("OPENAI_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    openai_status = "✅" if openai_key else "❌"
    gemini_status = "✅" if gemini_key else "❌"
    
    print(f"{openai_status} OPENAI_API_KEY: {'Set' if openai_key else 'Not set'}")
    print(f"{gemini_status} GEMINI_API_KEY: {'Set' if gemini_key else 'Not set'}")
    
    return bool(openai_key and gemini_key)

def main():
    """Run all verification tests"""
    print("🚀 Hindi TTS Integration Verification")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Hindi Detection", test_hindi_detection),
        ("Command Processing", test_command_processing),
        ("Translation", test_translation),
        ("Environment Variables", test_environment)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your Hindi TTS integration is ready to use!")
        print("\nNext steps:")
        print("1. Start the backend server: python main.py")
        print("2. Run the Flutter app: flutter run -d web-server")
        print("3. Test with voice commands like 'hindi mein bolo'")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
