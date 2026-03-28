from flask import Flask, request, jsonify
from optimum.intel.openvino import OVModelForSpeechSeq2Seq
from transformers import AutoProcessor
import base64
import torch

MODEL_PATH = "/model"  # <-- path from init container

processor = AutoProcessor.from_pretrained(MODEL_PATH)
model = OVModelForSpeechSeq2Seq.from_pretrained(MODEL_PATH)

app = Flask(__name__)

@app.route("/transcribe", methods=["POST"])
def transcribe():
    audio_b64 = request.json["audio"]
    audio_bytes = base64.b64decode(audio_b64)

    # Optional: process in-memory (avoid temp file)
    import io
    import soundfile as sf

    audio, sr = sf.read(io.BytesIO(audio_bytes))
    inputs = processor(audio, sampling_rate=sr, return_tensors="pt")
    result = model.generate(**inputs)
    text = processor.batch_decode(result, skip_special_tokens=True)[0]

    return jsonify({"text": text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, threaded=True)
