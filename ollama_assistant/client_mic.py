from builtins import int, print
import io
import sounddevice as sd
import scipy.io.wavfile as wav

def record_audio(duration=5, fs=16000):
    print("Recording...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()  # Wait until recording is finished
    print("Recording complete.")

    # Save audio to in-memory wav file
    wav_io = io.BytesIO()
    wav.write(wav_io, fs, audio)
    wav_io.seek(0)  # reset pointer to the beginning
    return wav_io

import requests

API_URL = 'http://localhost:5000/ask'

def send_audio(audio_io):
    files = {'audio': ('input.wav', audio_io, 'audio/wav')}
    response = requests.post(API_URL, files=files)
    
    if response.ok:
        print("AI response: ", response.json().get('response', 'No response found'))
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None
    
if __name__ == "__main__":
    audio_data = record_audio(duration=5)  # Record 5 seconds; adjust if needed
    send_audio(audio_data)
