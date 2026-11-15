#!/usr/bin/env python3
"""Check that everything the editing workflow needs is installed.

    python tools/check_setup.py
"""
import shutil
import subprocess
import sys

from common import FONTS, REPO, font_files

FILTERS = ["ass", "xfade", "acrossfade", "sidechaincompress", "loudnorm", "ebur128", "lut3d", "eq"]
ok = True


def report(good: bool, label: str, fix: str = "") -> None:
    global ok
    ok &= good
    print(f"  [{'OK' if good else '!!'}] {label}" + ("" if good else f"\n       -> {fix}"))


print("Checking setup...\n")
report(sys.version_info >= (3, 9), f"Python {sys.version.split()[0]}", "install Python 3.9 or newer from python.org")

for tool in ("ffmpeg", "ffprobe"):
    report(shutil.which(tool) is not None, tool, "install FFmpeg (see README) and reopen the terminal")
if shutil.which("ffmpeg"):
    ver = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True).stdout.split("\n")[0]
    print(f"       {ver[:70]}")
    have = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True).stdout
    missing = [f for f in FILTERS if f" {f} " not in have]
    report(not missing, "FFmpeg filters" + (f" (missing: {', '.join(missing)})" if missing else ""),
           "install a 'full' FFmpeg build (gyan.dev 'full' on Windows, Homebrew on Mac)")

try:
    import faster_whisper  # noqa: F401
    report(True, "faster-whisper (speech to text)")
except ImportError:
    report(False, "faster-whisper (speech to text)", "pip install -r requirements.txt   (only needed for captions)")

try:
    import yt_dlp  # noqa: F401
    report(True, "yt-dlp (download videos from links)")
except ImportError:
    report(False, "yt-dlp (download videos from links)", "pip install -r requirements.txt")

try:
    import gdown  # noqa: F401
    report(True, "gdown (Google Drive links)")
except ImportError:
    report(False, "gdown (Google Drive links)", "pip install -r requirements.txt")

try:
    import rembg  # noqa: F401
    report(True, "rembg (product cutouts)")
except ImportError:
    report(False, "rembg (product cutouts)", "pip install -r requirements.txt")

fonts = font_files()
report(bool(fonts), f"fonts in {FONTS.relative_to(REPO)}/: {len(fonts)} found",
       "put .ttf/.otf files in the fonts/ folder (see README)")
if fonts:
    if shutil.which("fc-scan"):
        for f in fonts:
            fam = subprocess.run(["fc-scan", "--format", "%{family[0]}", str(f)], capture_output=True, text=True).stdout
            print(f"       {f.relative_to(REPO)}  ->  font name: \"{fam.strip()}\"")
    else:
        for f in fonts:
            print(f"       {f.relative_to(REPO)}")

print("\nAll good!" if ok else "\nFix the [!!] items above, then run this again.")
sys.exit(0 if ok else 1)
