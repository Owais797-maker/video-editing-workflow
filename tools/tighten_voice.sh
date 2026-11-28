#!/usr/bin/env bash
# Sharp silence cut for AI voice-overs (owner 2026-11-28: "sharply kat karna, fancy lage"):
# every pause longer than 0.12 s is cut down to ~0.08 s, leading silence removed. 48 kHz out.
# Usage: tools/tighten_voice.sh in.wav out.wav
set -e
ffmpeg -v error -y -i "$1" -af "silenceremove=start_periods=1:start_threshold=-35dB:stop_periods=-1:stop_duration=0.12:stop_threshold=-35dB:stop_silence=0.08,aresample=48000" "$2"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$2"
