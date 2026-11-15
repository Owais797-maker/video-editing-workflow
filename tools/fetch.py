#!/usr/bin/env python3
"""Download videos/music from links into a project.

    python tools/fetch.py "<link>" --project my-reel --to raw         # your footage / music
    python tools/fetch.py "<link>" --project my-reel --to reference   # inspiration video

Supported links:
  - Google Drive: a shared file OR a whole shared folder ("Anyone with the link")
  - Dropbox shared links, and direct links to .mp4/.mov/.mp3 files
  - Instagram, TikTok, Facebook, X/Twitter, Vimeo ... (via yt-dlp)
    YouTube usually refuses downloads from cloud servers; screen-record it instead.

Reference downloads are analysed automatically (tools/analyze.py).
Reference videos are for studying style only: never reuse their footage or music.
"""
import argparse
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

from common import EDITS, REPO, VIDEO_EXT, die

AUDIO_EXT = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}
MEDIA_EXT = VIDEO_EXT | AUDIO_EXT | {".png", ".jpg", ".jpeg", ".webp", ".heic", ".cube"}


class _Quiet:
    def debug(self, msg): pass
    def info(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass


def snapshot(d: Path) -> set:
    return {p for p in d.rglob("*") if p.is_file()}


def google_drive(url: str, dest: Path) -> None:
    try:
        import gdown
    except ImportError:
        die("gdown is not installed. Run: pip install -r requirements.txt")
    m = re.search(r"/folders/([\w-]+)", url)
    if m:
        res = gdown.download_folder(id=m.group(1), output=str(dest), quiet=True)
        if not res:
            raise RuntimeError("folder is empty or not shared as 'Anyone with the link'")
    else:
        m = re.search(r"/d/([\w-]+)", url) or re.search(r"[?&]id=([\w-]+)", url)
        if not m:
            raise RuntimeError("could not find the file id in this Google Drive link")
        res = gdown.download(id=m.group(1), output=str(dest) + "/", quiet=True)
        if not res:
            raise RuntimeError("file not shared as 'Anyone with the link', or Drive's download limit was hit")


def direct(url: str, dest: Path) -> None:
    if "dropbox.com" in url:
        url = re.sub(r"([?&])dl=0", r"\1dl=1", url)
        if "dl=1" not in url:
            url += ("&" if "?" in url else "?") + "dl=1"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        name = None
        cd = r.headers.get("Content-Disposition", "")
        m = re.search(r"filename\*=UTF-8''([^;]+)", cd) or re.search(r'filename="?([^";]+)', cd)
        if m:
            name = urllib.parse.unquote(m.group(1))
        name = Path(name or Path(urllib.parse.urlparse(r.url).path).name or "download.mp4").name
        if name.endswith(".zip"):
            raise RuntimeError("this is a zip/folder link; share the files one by one or use Google Drive")
        with open(dest / name, "wb") as f:
            while chunk := r.read(1 << 20):
                f.write(chunk)


def social(url: str, dest: Path, cookies: str | None) -> None:
    try:
        import yt_dlp
    except ImportError:
        die("yt-dlp is not installed. Run: pip install -r requirements.txt")
    opts = {
        "outtmpl": str(dest / "%(extractor)s-%(id)s.%(ext)s"),
        "format": "bv*[height<=1920][ext=mp4]+ba[ext=m4a]/bv*[height<=1920]+ba/b",
        "merge_output_format": "mp4", "noplaylist": True, "quiet": True, "no_warnings": True,
        "restrictfilenames": True, "logger": _Quiet(),
        "writeinfojson": False,
    }
    if cookies:
        opts["cookiesfrombrowser"] = (cookies,)
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.extract_info(url, download=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("urls", nargs="+")
    ap.add_argument("--project", required=True)
    ap.add_argument("--to", choices=["raw", "reference"], required=True)
    ap.add_argument("--cookies-from", metavar="BROWSER", help="only on a computer: chrome, edge, firefox, safari")
    ap.add_argument("--no-analyze", action="store_true")
    args = ap.parse_args()

    dest = EDITS / ("Raw" if args.to == "raw" else "Reference") / args.project
    dest.mkdir(parents=True, exist_ok=True)
    new_files: list[Path] = []
    failed = 0
    for url in args.urls:
        before = snapshot(dest)
        host = urllib.parse.urlparse(url).netloc.lower()
        print(f"Downloading {url} ...")
        try:
            if "drive.google.com" in host or "docs.google.com" in host:
                google_drive(url, dest)
            elif "dropbox" in host or Path(urllib.parse.urlparse(url).path).suffix.lower() in MEDIA_EXT:
                direct(url, dest)
            else:
                social(url, dest, args.cookies_from)
        except Exception as e:  # noqa: BLE001
            failed += 1
            msg = re.sub(r"\x1b\[[0-9;]*m", "", str(e)).strip()
            if "youtube" in host or "youtu.be" in host:
                msg += "\n     YouTube blocks cloud servers: screen-record the video on your phone and share it via Google Drive."
            print(f"  !! failed: {msg[:400]}")
            continue
        got = sorted(snapshot(dest) - before)
        for p in got:
            print(f"  + {p.relative_to(REPO)}  ({p.stat().st_size / 1e6:.1f} MB)")
        new_files += got
        if not got:
            print("  (nothing new: the file may already be there)")

    if args.to == "reference" and not args.no_analyze:
        for p in new_files:
            if p.suffix.lower() in VIDEO_EXT:
                subprocess.run([sys.executable, str(Path(__file__).with_name("analyze.py")), str(p), "--project", args.project])
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
