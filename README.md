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

## Available Languages & How To Specify Them

Piper publishes voices for dozens of languages. The table below lists the most common language codes you can reference in `voices.json` (see the [official catalogue](https://huggingface.co/rhasspy/piper-voices/tree/v1.0.0) for the latest list and models per dialect):

| Code | Language           | Example voice path                              |
|------|--------------------|------------------------------------------------|
| ar   | Arabic             | `ar/ar_EG/ayman/...`                           |
| ca   | Catalan            | `ca/ca_ES/guifrem/...`                         |
| cs   | Czech              | `cs/cs_CZ/jirka/...`                           |
| da   | Danish             | `da/da_DK/jeppe/...`                           |
| de   | German             | `de/de_DE/kerstin/...`                         |
| el   | Greek              | `el/el_GR/rapunzelina/...`                     |
| en   | English (various)  | `en/en_US/lessac/...`, `en/en_GB/cori/...`     |
| es   | Spanish            | `es/es_ES/sharvard/...`, `es/es_MX/aldona/...` |
| fi   | Finnish            | `fi/fi_FI/jenny/...`                           |
| fr   | French             | `fr/fr_FR/gilles/...`                          |
| gl   | Galician           | `gl/gl_ES/roxana/...`                          |
| hr   | Croatian           | `hr/hr_HR/tihomir/...`                         |
| hu   | Hungarian          | `hu/hu_HU/imre/...`                            |
| id   | Indonesian         | `id/id_ID/izza/...`                            |
| is   | Icelandic          | `is/is_IS/salka/...`                           |
| it   | Italian            | `it/it_IT/riccardo/...`                        |
| ja   | Japanese           | `ja/ja_JP/miku/...`                            |
| ko   | Korean             | `ko/ko_KR/tomoko/...`                          |
| lt   | Lithuanian         | `lt/lt_LT/alda/...`                            |
| lv   | Latvian            | `lv/lv_LV/egita/...`                           |
| nb   | Norwegian Bokmål   | `nb/nb_NO/kari/...`                            |
| nl   | Dutch              | `nl/nl_NL/nikolaas/...`                        |
| pl   | Polish             | `pl/pl_PL/daniel/...`                          |
| pt   | Portuguese         | `pt/pt_PT/joana/...`                           |
| ro   | Romanian           | `ro/ro_RO/george/...`                          |
| ru   | Russian            | `ru/ru_RU/irinia/...`                          |
| sk   | Slovak             | `sk/sk_SK/adam/...`                            |
| sl   | Slovenian          | `sl/sl_SI/tatjana/...`                         |
| sr   | Serbian            | `sr/sr_RS/vuk/...`                             |
| sv   | Swedish            | `sv/sv_SE/anders/...`                          |
| tr   | Turkish            | `tr/tr_TR/ahmet/...`                           |
| uk   | Ukrainian          | `uk/uk_UA/natalia/...`                         |
| vi   | Vietnamese         | `vi/vi_VN/son/...`                             |
| yue  | Cantonese          | `yue/yue_HK/jyutping/...`                      |

> Piper also ships additional languages (Afrikaans, Bengali, Hindi, Malayalam, Tamil, Thai, Urdu, etc.). For anything not in the table, inspect the Hugging Face tree and mirror the directory layout in your `voices.json` entry.

### Selecting a Voice

1. **Automatic (recommended)** – leave `--model` unset. The script reads `DC.language`, reduces it to the short code (`es`, `en`, etc.), and looks up the matching entry in `voices.json` based on the requested `--gender`.
2. **Manual voice** – pass `--model /path/to/model.onnx`. Optionally also provide `--speaker 1` if the chosen model contains multiple speakers.
3. **Adding languages** – edit `voices.json` and insert a new entry:

   ```jsonc
   "pt": {
     "female": {
       "name": "pt_PT-joana-medium",
       "url": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/pt/pt_PT/joana/medium/pt_PT-joana-medium.onnx",
       "speaker_id": null
     }
   }
   ```

   After saving, run the converter again. The first execution will download the `.onnx`/`.json` pair automatically into `piper_tts/`.

If an EPUB uses a language that is not present in `voices.json`, the converter falls back to English and logs a warning. Add the missing language or specify `--model` to override.

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
