import requests
import json

models_to_check = [
    "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx.json",
    "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json",
    "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/ryan/medium/en_US-ryan-medium.onnx.json",
    "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/davefx/medium/es_ES-davefx-medium.onnx.json"
]

for url in models_to_check:
    print(f"Checking {url.split('/')[-1]}...")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if "speaker_id_map" in data and data["speaker_id_map"]:
                print(f"  Multi-speaker detected: {data['speaker_id_map']}")
            else:
                print("  Single speaker.")
        else:
            print(f"  Failed to download: {response.status_code}")
    except Exception as e:
        print(f"  Error: {e}")
