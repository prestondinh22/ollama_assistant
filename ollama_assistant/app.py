from builtins import print
from flask import Flask, request, jsonify
import utils.whisper_wrapper 
from utils.ollama_wrapper import ask_ollama
import os
import uuid

app = Flask(__name__)

@app.route('/ask', methods=['POST'])
def ask():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
    
    audio_file = request.files["audio"]
    temp_path = f"/tmp/{uuid.uuid4()}.wav"
    audio_file.save(temp_path)

    prompt = utils.whisper_wrapper.transcribe_audio(temp_path)
    print('User said: ', prompt)

    response = ask_ollama(prompt)
    print(f"Assistant: {response}")

    os.remove(temp_path)
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
