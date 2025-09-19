import sounddevice as sd
import numpy as np
import queue    
import threading
import os
import librosa
from faster_whisper import WhisperModel

# settings - optimized for command recognition
samplerate = 16000
block_duration = 0.25 # secs - smaller blocks for better responsiveness
chunk_duration = 3 # secs - longer chunks for better context
channels = 1

frames_per_block = int(samplerate * block_duration)
frames_per_chunk = int(samplerate * chunk_duration)

audio_queue = queue.Queue()
audio_buffer = []

# model setup - use CPU for better compatibility
model = WhisperModel("small", device="cpu", compute_type="int8")

def audio_callback(indata, frames, time, status):
    if status:
        print(f"Status: {status}")
    audio_queue.put(indata.copy())

def recorder():
    with sd.InputStream(samplerate=samplerate, channels=channels, callback=audio_callback, blocksize=frames_per_block):
        print("Listning... Press Ctrl+C to stop")
        while True:
            sd.sleep(100)

def transcriber():
    global audio_buffer
    while True:
        block = audio_queue.get()
        audio_buffer.append(block)

        total_frames = sum(len(b) for b in audio_buffer)
        if total_frames >= frames_per_chunk:
            audio_data = np.concatenate(audio_buffer)[:frames_per_chunk]
            audio_buffer = [] # buffer clear

            audio_data = audio_data.flatten().astype(np.float32)

            segments, _ = model.transcribe(
                audio_data,
                language="en", 
                beam_size=1,
                vad_filter=True,  # Enable voice activity detection
                vad_parameters=dict(min_silence_duration_ms=500)
            )
            for segment in segments:
                text = segment.text.strip()
                if text:  # Only print non-empty segments
                    print(f"Transcribed: {text}")
                    # You can add additional processing here for command recognition

def transcribe(audio_file_path):
    """
    Transcribe an audio file using Whisper model.
    
    Args:
        audio_file_path (str): Path to the audio file
        
    Returns:
        str: Transcribed text
    """
    try:
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
        
        # Load audio file using librosa
        audio_data, sr = librosa.load(audio_file_path, sr=16000, mono=True)
        
        # Transcribe using Whisper with improved settings
        segments, _ = model.transcribe(
            audio_data, 
            language="en", 
            beam_size=1,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500)
        )
        
        # Combine all segments into a single text
        full_text = ""
        for segment in segments:
            full_text += segment.text + " "
        
        return full_text.strip()
        
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return ""

def start_realtime_transcription():
    """Start real-time transcription (for standalone use)"""
    threading.Thread(target=recorder, daemon=True).start()
    transcriber()

# Only start real-time transcription if this file is run directly
if __name__ == "__main__":
    start_realtime_transcription()