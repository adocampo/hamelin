import argparse
import os
import re
import subprocess
import sys
from bs4 import BeautifulSoup
import ebooklib
from ebooklib import epub
from voice_manager import VoiceManager

def extract_text_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    text_parts = []
    
    # Process block-level elements to ensure pauses
    # Common block elements in EPUBs
    block_elements = ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'blockquote']
    
    # Only look inside the body tag if it exists
    root = soup.body if soup.body else soup

    for element in root.find_all(text=True):
        # Skip XML declarations or processing instructions that might be captured as text
        if element.strip().startswith('xml version='):
            continue

        parent = element.parent
        if parent.name in ['script', 'style', 'title', 'meta']:
            continue
            
        clean_text = element.strip()
        if not clean_text:
            continue
            
        # Check if this text is part of a block element
        is_block = False
        curr = parent
        while curr and curr.name != 'body':
            if curr.name in block_elements:
                is_block = True
                break
            curr = curr.parent
            
        if is_block:
            # Ensure it ends with punctuation for TTS pause
            if clean_text[-1] not in '.!?":;':
                clean_text += '.'
        
        # Split on ellipses to force standalone segments, which creates natural pauses
        segments = re.split(r'(\.\.\.)', clean_text)
        for segment in segments:
            segment = segment.strip()
            if not segment:
                continue
            if segment == '...':
                text_parts.append('...')
                text_parts.append('')
                continue
            if segment[-1] not in '.!?":;':
                segment += '.'
            text_parts.append(segment)

    return "\n".join(text_parts)

def convert_text_to_audio(text, output_file, piper_binary, model_path, speaker_id=None):
    if not text:
        return False
    
    cmd = [
        piper_binary,
        '--model', model_path,
        '--output_file', output_file
    ]
    
    if speaker_id is not None:
        cmd.extend(['--speaker', str(speaker_id)])
    
    try:
        # Piper expects input from stdin
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input=text)
        
        if process.returncode != 0:
            print(f"Error running piper: {stderr}")
            return False
        return True
    except Exception as e:
        print(f"Exception running piper: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Convert EPUB to Audio using Piper TTS")
    parser.add_argument("epub_file", help="Path to the EPUB file")
    parser.add_argument("--piper", required=True, help="Path to the piper binary")
    parser.add_argument("--model", help="Path to the piper voice model (.onnx). If not provided, auto-detected.")
    parser.add_argument("--speaker", type=int, help="Speaker ID (for multi-speaker models)")
    parser.add_argument("--gender", default="female", choices=["male", "female"], help="Preferred voice gender (if auto-detecting)")
    parser.add_argument("--output-dir", default="output", help="Directory to save audio files")
    parser.add_argument("--mp3", action="store_true", help="Convert output to MP3 (requires ffmpeg)")
    
    args = parser.parse_args()

    if not os.path.exists(args.epub_file):
        print(f"EPUB file not found: {args.epub_file}")
        sys.exit(1)

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    print(f"Reading EPUB: {args.epub_file}")
    try:
        book = epub.read_epub(args.epub_file)
    except Exception as e:
        print(f"Error reading EPUB: {e}")
        sys.exit(1)

    # Determine Voice Model
    model_path = args.model
    speaker_id = args.speaker
    
    if not model_path:
        # Try to detect language
        langs = book.get_metadata('DC', 'language')
        lang_code = 'en' # Default
        if langs:
            lang_code = langs[0][0]
            print(f"Detected Language: {lang_code}")
        
        vm = VoiceManager()
        model_path, detected_speaker_id = vm.get_model_path(lang_code, args.gender)
        
        if not model_path:
            print("Could not find or download a suitable voice model.")
            sys.exit(1)
            
        if speaker_id is None:
            speaker_id = detected_speaker_id
            
        print(f"Using Voice Model: {model_path}")
        if speaker_id is not None:
            print(f"Using Speaker ID: {speaker_id}")

    playlist_path = os.path.join(args.output_dir, "playlist.m3u")
    playlist_entries = []

    chapter_count = 0
    
    # Iterate through the spine to get the reading order
    for item_id in book.spine:
        item = book.get_item_with_id(item_id[0])
        
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            content = item.get_content()
            text = extract_text_from_html(content)
            
            if len(text) < 50: # Skip very short sections (likely TOC or empty)
                print(f"Skipping short section: {item.get_name()}")
                continue

            chapter_count += 1
            wav_filename = f"chapter_{chapter_count:03d}.wav"
            wav_path = os.path.join(args.output_dir, wav_filename)
            
            print(f"Processing Chapter {chapter_count}...")
            success = convert_text_to_audio(text, wav_path, args.piper, model_path, speaker_id)
            
            if success:
                if args.mp3:
                    mp3_filename = f"chapter_{chapter_count:03d}.mp3"
                    mp3_path = os.path.join(args.output_dir, mp3_filename)
                    print(f"Converting to MP3: {mp3_filename}")
                    try:
                        subprocess.run(
                            ['ffmpeg', '-y', '-i', wav_path, '-codec:a', 'libmp3lame', '-qscale:a', '2', mp3_path],
                            check=True,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                        os.remove(wav_path)
                        playlist_entries.append(mp3_filename)
                    except Exception as e:
                        print(f"Error converting to MP3: {e}")
                        # Fallback to WAV if conversion fails
                        playlist_entries.append(wav_filename)
                else:
                    playlist_entries.append(wav_filename)
            else:
                print(f"Failed to convert Chapter {chapter_count}")

    # Create M3U playlist
    with open(playlist_path, 'w') as f:
        f.write("#EXTM3U\n")
        for entry in playlist_entries:
            f.write(f"{entry}\n")

    print(f"Done! Audio files and playlist saved to {args.output_dir}")

if __name__ == "__main__":
    main()
