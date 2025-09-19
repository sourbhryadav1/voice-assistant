# Voice Assistant with Hindi TTS Integration

A comprehensive voice assistant application with advanced Hindi Text-to-Speech (TTS) capabilities, built with Python Flask backend and Flutter frontend.

## 🌟 Features

### Core Functionality
- **Voice Recognition**: Real-time speech-to-text using OpenAI Whisper
- **Text-to-Speech**: High-quality TTS with multiple voice options
- **Hindi Language Support**: Complete Hindi TTS integration
- **Command Processing**: Intelligent voice command recognition
- **Translation Services**: English to Hindi translation using Gemini AI
- **Web Interface**: Flutter-based responsive web application

### Hindi TTS Features
- **Automatic Hindi Detection**: Detects Hindi words and phrases in user input
- **Smart Voice Selection**: Automatically switches to optimal voice for Hindi
- **Bilingual Commands**: Supports both English and Hindi voice commands
- **Real-time Translation**: Instant English to Hindi translation
- **Cultural Context**: Natural Hindi responses with proper pronunciation

## 🏗️ Project Structure

```
deshpande_main/
├── backend/                    # Python Flask Backend
│   ├── main.py                # Main Flask application
│   ├── tts.py                 # Text-to-Speech module with Hindi support
│   ├── stt.py                 # Speech-to-Text module
│   ├── command_processor.py   # Voice command processing
│   ├── summarizer_service.py  # AI summarization and translation
│   ├── hindi_demo.py          # Demo script for Hindi features
│   └── test/                  # Test files
│       ├── test_hindi_tts.py  # Hindi TTS testing
│       ├── test_voice_recognition.py
│       └── hindi_test.mp3     # Test audio files
├── flutter_app/               # Flutter Frontend
│   ├── lib/
│   │   ├── main.dart         # Main Flutter app
│   │   └── home_screen.dart  # Home screen UI
│   ├── pubspec.yaml          # Flutter dependencies
│   └── web/                  # Web build files
├── env/                      # Python virtual environment
├── whisper/                  # Whisper model files
└── requirements.txt          # Python dependencies
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Flutter SDK
- OpenAI API Key
- Gemini API Key

### Backend Setup

1. **Clone and navigate to project**
   ```bash
   cd voice-assistant
   ```

2. **Activate virtual environment**
   ```bash
   # Windows
   .\env\Scripts\Activate.ps1
   
   # Linux/Mac
   source env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the backend directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-1.5-flash
   ```

5. **Run the backend server**
   ```bash
   cd backend
   python main.py
   ```
   Server will start at `http://localhost:5000`

### Frontend Setup

1. **Navigate to Flutter app**
   ```bash
   cd flutter_app
   ```

2. **Install Flutter dependencies**
   ```bash
   flutter pub get
   ```

3. **Run Flutter app**
   ```bash
   flutter run -d web-server --web-port 3000
   ```

## 🎯 Usage Examples

### Hindi Voice Commands

The assistant recognizes various Hindi commands:

**English Commands:**
- "hindi mein bolo" (speak in Hindi)
- "translate to hindi"
- "hindi me kaho" (say in Hindi)
- "speak in hindi"

**Hindi Commands:**
- "हिंदी में बताओ" (tell in Hindi)
- "हिंदी में बोलो" (speak in Hindi)
- "हिंदी मे कहो" (say in Hindi)

### API Endpoints

#### Voice Recognition
```http
POST /api/voice
Content-Type: multipart/form-data

# Upload audio file with 'audio' field
```

#### Text-to-Speech
```http
POST /api/tts
Content-Type: application/json

{
  "text": "Hello, this is a test",
  "voice": "alloy",
  "is_hindi": false
}
```

#### Hindi Response (Translation + TTS)
```http
POST /api/hindi-response
Content-Type: application/json

{
  "text": "You can navigate to different sections",
  "original_text": "You can navigate to different sections"
}
```

#### Summarization with Hindi Translation
```http
POST /api/summarize
Content-Type: application/json

{
  "text": "Your text here",
  "translate_to_hindi": true
}
```

## 🧪 Testing

### Run Hindi TTS Demo
```bash
cd backend
python hindi_demo.py
```

### Run Comprehensive Tests
```bash
cd backend/test
python test_hindi_tts.py
```

### Test Individual Components
```bash
# Test TTS functionality
python tts.py "Hello, this is a test"

# Test command processing
python command_processor.py

# Test Hindi detection
python -c "from tts import detect_hindi_in_text; print(detect_hindi_in_text('hindi mein bolo'))"
```

## 🔧 Configuration

### Voice Settings
- **English Voice**: `alloy` (default)
- **Hindi Voice**: `nova` (optimized for Hindi pronunciation)
- **Model**: `gpt-4o-mini-tts`

### Hindi Detection Patterns
The system detects Hindi through:
- Devanagari script characters (Unicode range: U+0900-U+097F)
- Common Hindi words: `hindi`, `bolo`, `batao`, `kya`, `kaise`, etc.
- Mixed language phrases: `hindi mein bolo`, `hindi me kaho`

### Command Processing
- **Confidence Threshold**: 0.3 (minimum for valid commands)
- **Supported Commands**: help, navigation, action, search, stop, repeat, volume, time, weather, hindi
- **Noise Filtering**: Removes filler words like "um", "uh", "like"

## 🌐 API Documentation

### Response Formats

#### Voice Command Response
```json
{
  "text": "hindi mein bolo",
  "command": {
    "type": "hindi",
    "confidence": 0.90,
    "suggestions": ["I'll translate the response to Hindi and speak it aloud."]
  },
  "is_valid": true,
  "wants_hindi": true
}
```

#### TTS Response
- Returns MP3 audio file
- Content-Type: `audio/mpeg`
- Optimized voice selection based on language detection

## 🛠️ Development

### Adding New Hindi Commands
Edit `backend/command_processor.py`:
```python
'hindi': [
    r'\b(your_new_pattern)\b',
    # Add more patterns here
]
```

### Customizing Hindi Detection
Edit `backend/tts.py`:
```python
hindi_words = [
    'your_new_hindi_word',
    # Add more words here
]
```

### Adding New API Endpoints
Add to `backend/main.py`:
```python
@app.post('/api/your-endpoint')
def your_endpoint():
    # Your implementation
    pass
```

## 📦 Dependencies

### Backend Dependencies
- `flask`: Web framework
- `flask-cors`: CORS support
- `openai`: AI services
- `google-generativeai`: Gemini AI integration
- `playsound`: Audio playback
- `python-dotenv`: Environment variables
- `requests`: HTTP requests

### Frontend Dependencies
- `flutter`: UI framework
- `http`: API communication
- `audioplayers`: Audio playback

## 🐛 Troubleshooting

### Common Issues

1. **Module Import Errors**
   ```bash
   # Ensure virtual environment is activated
   .\env\Scripts\Activate.ps1
   ```

2. **API Key Errors**
   - Verify `.env` file exists in backend directory
   - Check API keys are valid and have proper permissions

3. **Audio Playback Issues**
   - Ensure audio drivers are working
   - Check file permissions for temporary audio files

4. **Hindi TTS Not Working**
   - Verify OpenAI API key has TTS access
   - Check internet connection for API calls

### Debug Mode
Run backend in debug mode:
```bash
cd backend
python main.py
# Debug mode is enabled by default
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for Whisper and TTS services
- Google for Gemini AI translation
- Flutter team for the UI framework
- Python community for excellent libraries

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the API documentation

---

**Made with ❤️ for seamless Hindi-English voice interaction**
