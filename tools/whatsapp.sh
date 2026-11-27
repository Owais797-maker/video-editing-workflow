#!/usr/bin/env bash
# WhatsApp status / Facebook-safe copy: 1080x1920 H.264 High, 30 fps, ~8 Mbps capped, AAC 128k, faststart.
# WhatsApp/Facebook re-compress less when the file is already this size, so it stays sharper than a 4K upload.
# Usage: tools/whatsapp.sh "<master>.mp4"   -> "<master>-whatsapp.mp4"
set -e
in="$1"; out="${in%.mp4}-whatsapp.mp4"
ffmpeg -v error -y -i "$in" -vf "scale=1080:1920:force_original_aspect_ratio=decrease:flags=lanczos,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,fps=30" \
  -c:v libx264 -profile:v high -level 4.1 -preset slow -crf 19 -maxrate 8M -bufsize 16M -pix_fmt yuv420p \
  -c:a aac -b:a 128k -ar 44100 -movflags +faststart "$out"
echo "$out"
