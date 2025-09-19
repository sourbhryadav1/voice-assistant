from faster_whisper import WhisperModel

model_size = "small.en"


model = WhisperModel(model_size, device="cuda", compute_type="float16")

segments, _ = model.transcribe("speech.mp3",language="en", beam_size=5)

for segment in segments:
    print(segment.text)