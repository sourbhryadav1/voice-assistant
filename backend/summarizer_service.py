import os
from dotenv import load_dotenv
import requests
import json
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")


def summarize(text_input: str, translate_to_hindi: bool = False) -> str:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY not configured in environment/.env")

    prompt = f"""
You are a helpful voice assistant for a mobile app. The user has provided both their voice input and the current page context.

PAGE CONTEXT (JSON data about the current app page):
{text_input}

INSTRUCTIONS:
1. Analyze the page context to understand what page the user is on and what actions are available
2. Respond to the user's voice input in the context of the current page
3. If the user asks about navigation or actions, refer to the specific options available on this page
4. Keep responses concise (1-2 sentences) and actionable
5. Focus on what the user can actually do on this specific page

RESPONSE FORMAT:
- If user asks about page features: Describe what's available on this specific page
- If user asks for help: Provide context-aware help based on current page
- If user asks to navigate: Suggest available navigation options from this page
- If user asks general questions: Answer in the context of the current page

Remember: You have access to the complete page structure, so use it to provide accurate, context-aware responses.
"""



    model_name = "gemini-2.0-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
    headers = {
        'Content-Type': 'application/json',
        'x-goog-api-key': GEMINI_API_KEY
    }
    payload = {
        'contents': [
            {
                'parts': [{'text': prompt}]
            }
        ]
    }
    response = requests.post(url, headers=headers, json=payload, timeout=25)
    response.raise_for_status()

    data = response.json()
    candidate = data.get('candidates', [{}])[0]
    content = candidate.get('content', {}).get('parts', [{}])[0]
    ai_response = content.get('text', "")

    summary = ai_response.strip() or "🤖 Sorry, I couldn't get a response."
    
    # Translate to Hindi if requested
    if translate_to_hindi and summary != "🤖 Sorry, I couldn't get a response.":
        summary = translate_to_hindi_text(summary)
    
    return summary


def translate_to_hindi_text(text: str) -> str:
    """Translate English text to Hindi using Gemini"""
    if not GEMINI_API_KEY:
        return text  # Return original if no API key
    
    prompt = f"""
Translate the following English text to Hindi. Keep it natural and conversational for a voice assistant.
Only return the Hindi translation, no additional text or explanations.

Text to translate:
{text}
"""
    
    model_name = "gemini-2.0-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
    headers = {
        'Content-Type': 'application/json',
        'x-goog-api-key': GEMINI_API_KEY
    }
    payload = {
        'contents': [
            {
                'parts': [{'text': prompt}]
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        candidate = data.get('candidates', [{}])[0]
        content = candidate.get('content', {}).get('parts', [{}])[0]
        hindi_text = content.get('text', "").strip()
        
        return hindi_text or text  # Return original if translation fails
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Return original text if translation fails


# if __name__ == "__main__":
#     sample_transcript = '''{
#   "appName": "TaskMate",
#   "page": "Dashboard",
#   "header": {
#     "title": "Welcome Back, Sourabh!",
#     "subtitle": "Here’s a quick look at your productivity"
#   },
#   "navigation": [
#     { "label": "Home", "icon": "🏠", "route": "/home" },
#     { "label": "Tasks", "icon": "📝", "route": "/tasks" },
#     { "label": "Analytics", "icon": "📊", "route": "/analytics" },
#     { "label": "Settings", "icon": "⚙️", "route": "/settings" }
#   ],
#   "mainContent": {
#     "widgets": [
#       {
#         "title": "Today’s Tasks",
#         "items": [
#           { "task": "Finish sprint planning", "status": "pending" },
#           { "task": "Review pull requests", "status": "in-progress" },
#           { "task": "Update design docs", "status": "completed" }
#         ]
#       },
#       {
#         "title": "Quick Actions",
#         "buttons": [
#           { "label": "Add Task", "action": "navigate:/tasks/add" },
#           { "label": "Start Timer", "action": "start_timer" },
#           { "label": "Sync Data", "action": "sync_data" }
#         ]
#       }
#     ]
#   },
#   "footer": {
#     "text": "TaskMate © 2025",
#     "links": [
#       { "label": "Privacy Policy", "route": "/privacy" },
#       { "label": "Help", "route": "/help" }
#     ]
#   }
# }'''
#     def json_to_text(data):
#         text = f"{data['appName']} {data['page']} page: "
#         text += f"{data['header']['title']}. {data['header']['subtitle']}. "
#         nav_items = ', '.join([item['label'] for item in data['navigation']])
#         text += f"Navigation options include {nav_items}. "
#         for widget in data['mainContent']['widgets']:
#             items_text = ', '.join(item.get('task', item.get('label', '')) for item in widget.get('items', widget.get('buttons', [])))
#             text += f"{widget['title']} shows {items_text}. "
#         footer_links = ', '.join(link['label'] for link in data['footer']['links'])
#         text += f"Footer contains links like {footer_links}."
#         return text


#     print("--- Original Text ---")
#     data = json.loads(sample_transcript)
#     text_input = json_to_text(data)
#     print(text_input)
#     generated_summary = summarize(text_input)
#     print("\n--- Generated Summary ---")
#     print(generated_summary)