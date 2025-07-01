from builtins import int, print
import io
import sounddevice as sd
import scipy.io.wavfile as wav
import requests
from breadboard import wait_for_button_press, wait_for_button_release, control_led

def record_audio(duration=30, fs=16000):
    print("Waiting for button press to start recording...")
    control_led(False)  # Turn off LED initially
    
    # Wait for button press
    wait_for_button_press()
    print("Button pressed! Recording...")
    control_led(True)  # Turn on LED during recording
    
    # Start recording
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    
    # Wait for button release
    wait_for_button_release()
    print("Button released! Recording complete.")
    control_led(False)  # Turn off LED
    
    sd.stop()
   
    # Save audio to in-memory wav file
    wav_io = io.BytesIO()
    wav.write(wav_io, fs, audio)
    wav_io.seek(0)  # reset pointer to the beginning
    return wav_io


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
    print("Starting audio recording system...")
    print("Press the button to start recording, release to stop.")
    
    while True:
        try:
            audio_data = record_audio(duration=30)
            
            if audio_data:
                send_audio(audio_data)
                
        except KeyboardInterrupt:
            print("\nProgram terminated by user")
            control_led(False)  # Make sure LED is off
            break
        except Exception as e:
            print(f"Error occurred: {e}")
            control_led(False)  # Make sure LED is off