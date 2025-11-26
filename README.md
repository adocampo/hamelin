# EPUB Reader to Audio Converter

Tool for converting EPUB ebooks into chapterized audio files using [Piper TTS](https://github.com/rhasspy/piper). It automatically detects the book language, chooses an appropriate voice (including per-gender options), inserts pauses between paragraphs/blank lines, and even enforces natural breaks after ellipses (`...`). Optionally, outputs MP3 via `ffmpeg`.

## Features

- Converts each EPUB spine document into separate audio files (WAV or MP3) and produces a `playlist.m3u`.
- Automatically detects EPUB language (`DC.language`) and picks voice models accordingly.
- Supports multi-speaker voices (e.g., `es_ES-sharvard-medium`) via speaker IDs.
- Cleans HTML, ensures punctuation at paragraph ends, and inserts extra pauses for ellipses.
- Can download Piper voices on demand based on `voices.json`.
- Optional MP3 conversion (`ffmpeg` required).

## Requirements

- Python 3.10+
- [Piper TTS binary](https://github.com/rhasspy/piper/releases)
- `ffmpeg` (optional, only for MP3 output)

Python dependencies are listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Quick Start

1. **Install dependencies and prepare virtual environment**

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

2. **Download Piper binary and at least one voice model**

    ```bash
    ./download_piper.sh
    ```

    This script pulls the Linux x86_64 Piper binary and a default English voice into `piper_tts/`. You can also pre-download voices listed in `voices.json` or rely on the auto-download feature (see "Voice Management").

3. **Convert an EPUB**

    ```bash
    python epub_to_audio.py \
      libro.epub \
      --piper piper_tts/piper/piper \
      --output-dir output_audio \
      --mp3
    ```

    - Omit `--mp3` if you only need WAV.
    - Provide `--model` to override automatic voice selection.
    - Use `--speaker` to force a specific speaker ID when supplying your own model.

Generated files are stored in `output_audio/`, e.g.:

- `chapter_001.wav` / `chapter_001.mp3`
- `playlist.m3u`

## Voice Management

`voice_manager.py` uses `voices.json` to map languages (`en`, `es`) and genders to Piper voice URLs. On first use, if the model is missing under `piper_tts/`, it automatically downloads the `.onnx` and companion `.json` files.

Example entry:

```json
{
  "es": {
    "female": {
      "name": "es_ES-sharvard-medium",
      "url": "https://huggingface.co/rhasspy/piper-voices/.../es_ES-sharvard-medium.onnx",
      "speaker_id": 1
    }
  }
}
```

- `speaker_id` is optional; set when the model bundles multiple speakers.
- Add more languages/voices as needed.

## Text Processing Details

- Uses BeautifulSoup to extract readable text.
- Skips scripts, styles, metadata, and XML declarations.
- Ensures paragraphs end with punctuation to trigger Piper pauses.
- Adds blank lines after ellipses (`...`) to force longer silences.

## Troubleshooting

- **Missing Piper binary**: update `--piper` path or re-run `download_piper.sh`.
- **Voice download fails**: check URLs in `voices.json` or pre-download manually.
- **No voice for detected language**: edit `voices.json` to include that language or pass `--model` manually.
- **MP3 conversion errors**: confirm `ffmpeg` is installed (`which ffmpeg`).

## Future Work

- Detection of foreign-language words and code-switching.
- Integration hooks for Calibre-Web/Epub.js reader.
- Richer playlist metadata (timestamps, chapter titles).
