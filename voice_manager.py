import os
import json
import urllib.request
import sys

class VoiceManager:
    def __init__(self, base_dir="piper_tts", voices_file="voices.json"):
        self.base_dir = base_dir
        self.voices_file = voices_file
        self.voices_config = self._load_voices_config()
        
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    def _load_voices_config(self):
        if not os.path.exists(self.voices_file):
            print(f"Error: {self.voices_file} not found.")
            return {}
        with open(self.voices_file, 'r') as f:
            return json.load(f)

    def get_model_path(self, language_code, gender="female"):
        # Normalize language code (e.g., 'en-US' -> 'en')
        lang_short = language_code.split('-')[0].split('_')[0].lower()
        
        if lang_short not in self.voices_config:
            print(f"Warning: Language '{lang_short}' not found in config. Defaulting to 'en'.")
            lang_short = 'en'

        if gender not in self.voices_config[lang_short]:
             # Fallback to the other gender if the requested one isn't available
             available_genders = list(self.voices_config[lang_short].keys())
             if available_genders:
                 gender = available_genders[0]
                 print(f"Warning: Gender '{gender}' not found for '{lang_short}'. Using '{gender}'.")
             else:
                 return None, None

        voice_info = self.voices_config[lang_short][gender]
        model_name = voice_info['name']
        model_url = voice_info['url']
        speaker_id = voice_info.get('speaker_id')
        
        onnx_filename = f"{model_name}.onnx"
        json_filename = f"{model_name}.onnx.json"
        
        onnx_path = os.path.join(self.base_dir, onnx_filename)
        json_path = os.path.join(self.base_dir, json_filename)

        # Download if missing
        if not os.path.exists(onnx_path) or not os.path.exists(json_path):
            print(f"Downloading voice model: {model_name}...")
            try:
                self._download_file(model_url, onnx_path)
                self._download_file(model_url + ".json", json_path)
                print("Download complete.")
            except Exception as e:
                print(f"Error downloading voice: {e}")
                return None, None

        return onnx_path, speaker_id

    def _download_file(self, url, output_path):
        # Simple download with progress bar could be added here
        urllib.request.urlretrieve(url, output_path)
