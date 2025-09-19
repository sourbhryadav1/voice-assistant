#!/usr/bin/env python3
"""
Demo script showing how page data changes with different pages
"""
import json
from summarizer_service import summarize

def demo_home_page():
    """Demo home page data processing"""
    print("🏠 HOME PAGE DEMO")
    print("=" * 40)
    
    home_page_data = {
        'userInput': 'What can I do on this page?',
        'pageContext': {
            'appName': 'Flutter App',
            'page': 'Home',
            'header': {
                'title': 'Welcome to Flutter App',
                'subtitle': 'Your personal assistant is ready to help'
            },
            'content': {
                'featuredItems': [
                    {
                        'title': 'Welcome to Flutter App',
                        'subtitle': 'Your personal assistant is ready',
                        'icon': 'Icons.home',
                        'color': 'Colors.blue',
                    },
                    {
                        'title': 'Voice Assistant',
                        'subtitle': 'Tap the mic to interact',
                        'icon': 'Icons.mic',
                        'color': 'Colors.green',
                    }
                ],
                'sections': [
                    {
                        'name': 'Featured Items',
                        'count': 2,
                        'description': 'Main features and capabilities of the app'
                    },
                    {
                        'name': 'Voice Assistant',
                        'enabled': True,
                        'description': 'Interactive voice assistant for navigation and help'
                    }
                ]
            },
            'actions': {
                'appBar': [
                    {'icon': 'mic', 'label': 'Voice assistant for home page'}
                ]
            }
        }
    }
    
    print("📋 Home Page JSON Data:")
    print(json.dumps(home_page_data, indent=2))
    print("\n🤖 Processing with Gemini...")
    
    try:
        response = summarize(json.dumps(home_page_data), translate_to_hindi=False)
        print(f"✅ Home Page Response: {response}")
        return response
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def demo_settings_page():
    """Demo settings page data processing"""
    print("\n⚙️ SETTINGS PAGE DEMO")
    print("=" * 40)
    
    settings_page_data = {
        'userInput': 'What can I do on this page?',
        'pageContext': {
            'appName': 'Flutter App',
            'page': 'Settings',
            'header': {
                'title': 'Settings',
                'subtitle': 'Customize your app experience'
            },
            'content': {
                'settings': [
                    {
                        'name': 'Notifications',
                        'enabled': True,
                        'description': 'Receive push notifications and alerts',
                        'type': 'toggle'
                    },
                    {
                        'name': 'Dark Mode',
                        'enabled': False,
                        'description': 'Switch between light and dark themes',
                        'type': 'toggle'
                    },
                    {
                        'name': 'Language',
                        'value': 'English',
                        'description': 'Choose your preferred language',
                        'type': 'dropdown',
                        'options': ['English', 'Hindi', 'Spanish', 'French']
                    },
                    {
                        'name': 'Volume',
                        'value': 0.8,
                        'description': 'Adjust audio volume level',
                        'type': 'slider',
                        'min': 0.0,
                        'max': 1.0
                    }
                ],
                'sections': [
                    {
                        'name': 'Appearance',
                        'count': 2,
                        'description': 'Visual and theme settings'
                    },
                    {
                        'name': 'Audio',
                        'count': 1,
                        'description': 'Sound and volume settings'
                    },
                    {
                        'name': 'Notifications',
                        'count': 1,
                        'description': 'Alert and notification preferences'
                    }
                ]
            },
            'actions': {
                'appBar': [
                    {'icon': 'arrow_back', 'label': 'Go back to home'},
                    {'icon': 'mic', 'label': 'Voice assistant for settings page'}
                ],
                'navigation': [
                    {'type': 'back', 'label': 'Return to home page'},
                    {'type': 'save', 'label': 'Save current settings'}
                ]
            }
        }
    }
    
    print("📋 Settings Page JSON Data:")
    print(json.dumps(settings_page_data, indent=2))
    print("\n🤖 Processing with Gemini...")
    
    try:
        response = summarize(json.dumps(settings_page_data), translate_to_hindi=False)
        print(f"✅ Settings Page Response: {response}")
        return response
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def demo_hindi_translation():
    """Demo Hindi translation"""
    print("\n🇮🇳 HINDI TRANSLATION DEMO")
    print("=" * 40)
    
    home_data = {
        'userInput': 'hindi mein bolo - what can I do here?',
        'pageContext': {
            'appName': 'Flutter App',
            'page': 'Home',
            'header': {'title': 'Welcome to Flutter App', 'subtitle': 'Your personal assistant is ready to help'},
            'content': {'featuredItems': [], 'sections': []},
            'actions': {'appBar': [{'icon': 'mic', 'label': 'Voice assistant for home page'}]}
        }
    }
    
    print("📋 Requesting Hindi translation...")
    
    try:
        response = summarize(json.dumps(home_data), translate_to_hindi=True)
        print(f"✅ Hindi Response: {response}")
        return response
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    """Run all demos"""
    print("🎯 PAGE DATA DEMONSTRATION")
    print("=" * 50)
    print("This demo shows how the assistant processes different page contexts")
    print("and generates appropriate responses based on the current page.")
    print()
    
    # Demo home page
    home_response = demo_home_page()
    
    # Demo settings page
    settings_response = demo_settings_page()
    
    # Demo Hindi translation
    hindi_response = demo_hindi_translation()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    if home_response and settings_response:
        print("✅ SUCCESS: Different pages generate different responses!")
        print(f"\n🏠 Home Page: {home_response}")
        print(f"⚙️ Settings Page: {settings_response}")
        
        if home_response.lower() != settings_response.lower():
            print("\n🎉 The system correctly uses page context!")
        else:
            print("\n⚠️  Responses are similar - may need prompt tuning.")
    
    if hindi_response:
        print(f"\n🇮🇳 Hindi Translation: {hindi_response}")
    
    print("\n🎯 KEY FEATURES DEMONSTRATED:")
    print("   ✅ Page-specific JSON data generation")
    print("   ✅ Context-aware AI responses")
    print("   ✅ Different responses per page")
    print("   ✅ Hindi translation support")
    print("   ✅ Dynamic page data with navigation")

if __name__ == "__main__":
    main()
