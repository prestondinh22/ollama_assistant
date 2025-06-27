from faster_whisper import WhisperModel

# Load base gpu whisper model once

model = WhisperModel("base", compute_type='auto')

def transcribe_audio(audio_path):
    segments, _ = model.transcribe(audio_path)
    return ''.join([seg.text for seg in segments])