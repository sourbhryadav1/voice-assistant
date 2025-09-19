# Quick Start Guide - Hindi TTS Voice Assistant

## 🚀 Get Started in 3 Steps

### 1. Setup Environment
```bash
# Activate virtual environment
.\env\Scripts\Activate.ps1

# Install dependencies (if not already done)
pip install -r requirements.txt
```

### 2. Configure API Keys
Create `.env` file in `backend/` directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Run the Application

**Backend (Terminal 1):**
```bash
cd backend
python main.py
```

**Frontend (Terminal 2):**
```bash
cd flutter_app
flutter run -d web-server --web-port 3000
```

## 🎯 Test Hindi TTS

### Voice Commands to Try:
- "hindi mein bolo" (speak in Hindi)
- "हिंदी में बताओ" (tell in Hindi)
- "translate to hindi"
- "hindi me kaho" (say in Hindi)

### API Testing:
```bash
# Test Hindi detection
python -c "from tts import detect_hindi_in_text; print(detect_hindi_in_text('hindi mein bolo'))"

# Run verification
python verify_setup.py

# Run demo
python hindi_demo.py
```

## 📱 Access the App
- **Web Interface**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **API Health Check**: http://localhost:5000/api/health

## 🔧 Troubleshooting

### Common Issues:
1. **Module not found**: Ensure virtual environment is activated
2. **API errors**: Check your API keys in `.env` file
3. **Audio issues**: Verify audio drivers and permissions

### Verification:
Run `python verify_setup.py` to check all components.

## 📚 Full Documentation
See `README.md` for complete documentation and advanced features.

---
**Ready to use! 🎉**
