#!/bin/bash

# Create piper directory
mkdir -p piper_tts
cd piper_tts

# Download Piper binary (Linux x86_64)
echo "Downloading Piper..."
wget -O piper.tar.gz https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_x86_64.tar.gz
tar -xvf piper.tar.gz
rm piper.tar.gz

# Download a voice model (en_US-lessac-medium)
echo "Downloading Voice Model (en_US-lessac-medium)..."
wget -O en_US-lessac-medium.onnx https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx
wget -O en_US-lessac-medium.onnx.json https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json

echo "Done! Piper and voice model are in piper_tts/"
