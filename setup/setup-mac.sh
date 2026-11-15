#!/usr/bin/env bash
# One-time setup on a Mac. Run from the repo folder in Terminal:
#   bash setup/setup-mac.sh
# Installs Homebrew (if missing), FFmpeg, Python, the Python packages and the Whisper model.
set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v brew >/dev/null; then
  echo "Installing Homebrew (it may ask for your Mac password)..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  eval "$(/opt/homebrew/bin/brew shellenv 2>/dev/null || /usr/local/bin/brew shellenv)"
fi
command -v ffmpeg >/dev/null || brew install ffmpeg
command -v python3 >/dev/null || brew install python

echo "Installing Python packages (Whisper, yt-dlp)..."
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

echo "Downloading the Whisper 'medium' model (about 1.5 GB, one time)..."
.venv/bin/python -c "from faster_whisper import WhisperModel; WhisperModel('medium', device='cpu', compute_type='int8')"

.venv/bin/python tools/check_setup.py
echo
echo "Done. Run the tools with .venv/bin/python (Claude knows this)."
