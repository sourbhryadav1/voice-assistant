from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from summarizer_service import summarize, translate_to_hindi_text
from command_processor import process_voice_command, is_valid_voice_command
from tts import detect_hindi_in_text, play_hindi_speech
import os
import io
from dotenv import load_dotenv
from stt import transcribe as local_transcribe

load_dotenv()

app = Flask(__name__, static_url_path='', static_folder='.')
CORS(app)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

try:
    from openai import OpenAI
    openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
except Exception:
    openai_client = None


@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.get('/favicon.ico')
def favicon():
    return ('', 204)


@app.get('/api/health')
def health():
    return jsonify({"status": "ok"})


@app.post('/api/summarize')
def api_summarize():
    data = request.get_json(silent=True) or {}
    if 'text' not in data or not isinstance(data['text'], str) or not data['text'].strip():
        return jsonify({"detail": "No text provided"}), 400
    user_text = data['text']
    translate_to_hindi = data.get('translate_to_hindi', False)
    try:
        summary = summarize(user_text, translate_to_hindi=translate_to_hindi)
        return jsonify({"summary": summary, "is_hindi": translate_to_hindi})
    except Exception as e:
        return jsonify({"detail": str(e)}), 500


@app.post('/summarize')
def handle_summarization():
    data = request.get_json(silent=True) or {}
    if 'text' not in data or not isinstance(data['text'], str) or not data['text'].strip():
        return jsonify({"error": "No text provided"}), 400
    user_text = data['text']
    translate_to_hindi = data.get('translate_to_hindi', False)
    summary = summarize(user_text, translate_to_hindi=translate_to_hindi)
    return jsonify({"summary": summary, "is_hindi": translate_to_hindi})


@app.post('/api/voice')
def api_voice():
    if openai_client is None:
        return jsonify({"detail": "OpenAI not configured"}), 500
    print("--- /api/voice endpoint hit ---")

    if 'audio' not in request.files:
        print(">>> ERROR: The key 'audio' was NOT found in the request files.")
        print(">>> Make sure your front-end is sending a file with the field name 'audio'.")
        return jsonify({"detail": "No audio key in request.files"}), 400

    print("1. Found 'audio' key in the request.")
    audio_file = request.files['audio']

    if not audio_file or audio_file.filename == '':
        print(">>> ERROR: The audio file is empty or has no filename.")
        return jsonify({"detail": "Empty file"}), 400

    print("2. Audio file seems valid. Proceeding to save and process.")

    try:
        debug_audio_path = "uploaded_audio.wav" 
        audio_file.save(debug_audio_path)
        print(f"Saved uploaded audio for debugging at: {debug_audio_path}")
        audio_file.seek(0)
        raw = audio_file.read()
        if not raw:
            return jsonify({"detail": "Empty audio content"}), 400
        buf = io.BytesIO(raw)
        # Give BytesIO a name so the SDK infers content type/extension
        buf.name = audio_file.filename or 'voice.wav'
        buf.seek(0)

        transcript = openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=buf
        )
        user_text = getattr(transcript, 'text', '').strip()
        if not user_text:
            return jsonify({"detail": "Transcription failed"}), 500

        # Process the voice command
        command_result = process_voice_command(user_text)
        
        # Check if user wants Hindi response
        wants_hindi = detect_hindi_in_text(user_text) or command_result.get('type') == 'hindi'
        
        # Only return valid commands to reduce "random things" processing
        if is_valid_voice_command(user_text):
            return jsonify({
                "text": user_text,
                "command": command_result,
                "is_valid": True,
                "wants_hindi": wants_hindi
            })
        else:
            return jsonify({
                "text": user_text,
                "command": command_result,
                "is_valid": False,
                "message": "Command not recognized or too unclear",
                "wants_hindi": wants_hindi
            })
    except Exception as e:
        # Surface full error for easier debugging in dev
        return jsonify({"detail": f"STT error: {e}"}), 500


@app.post('/api/tts')
def api_tts():
    if openai_client is None:
        return jsonify({"detail": "OpenAI not configured"}), 500

    data = request.get_json(silent=True) or {}
    text = (data.get('text') or '').strip()
    voice = (data.get('voice') or 'alloy').strip()
    model = (data.get('model') or 'gpt-4o-mini-tts').strip()
    is_hindi = data.get('is_hindi', False)
    
    if not text:
        return jsonify({"detail": "No text provided"}), 400

    try:
        # Auto-detect Hindi if not explicitly set
        if not is_hindi:
            is_hindi = detect_hindi_in_text(text)
        
        # Adjust voice for Hindi text
        if is_hindi:
            voice = "nova"  # Nova voice works better with Hindi
        
        # For Hindi text, we might need to adjust voice or model settings
        # OpenAI TTS supports multiple languages including Hindi
        speech = openai_client.audio.speech.create(
            model=model,
            voice=voice,
            input=text,
            response_format="mp3"
        )
        audio_bytes = speech.read()
        buf = io.BytesIO(audio_bytes)
        buf.seek(0)
        return send_file(buf, mimetype='audio/mpeg', as_attachment=False, download_name='speech.mp3')
    except Exception as e:
        return jsonify({"detail": f"TTS error: {e}"}), 500


@app.post('/api/hindi-response')
def api_hindi_response():
    """Handle requests that need Hindi translation and TTS"""
    data = request.get_json(silent=True) or {}
    text = (data.get('text') or '').strip()
    original_text = data.get('original_text', text)
    
    if not text:
        return jsonify({"detail": "No text provided"}), 400

    try:
        # Translate to Hindi if not already in Hindi
        is_already_hindi = detect_hindi_in_text(text)
        if not is_already_hindi:
            hindi_text = translate_to_hindi_text(text)
        else:
            hindi_text = text
        
        # Generate TTS for Hindi text
        if openai_client:
            speech = openai_client.audio.speech.create(
                model="gpt-4o-mini-tts",
                voice="nova",  # Nova voice works well with Hindi
                input=hindi_text,
                response_format="mp3"
            )
            audio_bytes = speech.read()
            buf = io.BytesIO(audio_bytes)
            buf.seek(0)
            
            return send_file(
                buf, 
                mimetype='audio/mpeg', 
                as_attachment=False, 
                download_name='hindi_speech.mp3'
            )
        else:
            return jsonify({
                "hindi_text": hindi_text,
                "original_text": original_text,
                "audio_available": False,
                "message": "OpenAI not configured for TTS"
            })
            
    except Exception as e:
        return jsonify({"detail": f"Hindi response error: {e}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)