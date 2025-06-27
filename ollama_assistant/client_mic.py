from builtins import int, print
import io
import sounddevice as sd
import scipy.io.wavfile as wav
from breadboard import check_button

def record_audio(duration=30, fs=16000):
    button_monitor = check_button() # checks state
    print("Button pressed! Recording...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    
    recording_started = False
    while True:
        button_state = next(button_monitor)
        if button_state == 1 and not recording_started:
            recording_started = True
        elif button_state == 0 and recording_started:
            break
    
    print("Button released! Recording complete.")
    sd.stop()
    
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
    while True:
        audio_data = record_audio(duration=30)
        if audio_data:
            send_audio(audio_data)
