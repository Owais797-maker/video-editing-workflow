#!/usr/bin/env python3
"""Download an inspiration video from a link (YouTube, Instagram, TikTok, Facebook, X ...)
into the project's Reference folder, then analyse it.

    python tools/fetch_reference.py "https://www.instagram.com/reel/XXXX/" --project my-reel

For links that need you to be logged in (private posts, some Instagram reels), add
--cookies-from chrome   (or edge / firefox / safari) to use your browser's login.

Reference videos are for studying the editing style only. Don't reuse other
people's footage or music in your own video.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from common import EDITS, REPO, die, need


class _Quiet:
    def debug(self, msg): pass
    def info(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("urls", nargs="+")
    ap.add_argument("--project", required=True)
    ap.add_argument("--cookies-from", metavar="BROWSER", help="chrome, edge, firefox, safari, brave")
    ap.add_argument("--no-analyze", action="store_true")
    args = ap.parse_args()
    need("ffmpeg")
    try:
        import yt_dlp
    except ImportError:
        die("yt-dlp is not installed. Run: pip install -r requirements.txt")

    dest = EDITS / "Reference" / args.project
    dest.mkdir(parents=True, exist_ok=True)
    for url in args.urls:
        opts = {
            "outtmpl": str(dest / "%(extractor)s-%(id)s.%(ext)s"),
            "format": "bv*[height<=1920][ext=mp4]+ba[ext=m4a]/bv*[height<=1920]+ba/b",
            "merge_output_format": "mp4",
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "restrictfilenames": True,
            "logger": _Quiet(),
        }
        if args.cookies_from:
            opts["cookiesfrombrowser"] = (args.cookies_from,)
        print(f"Downloading {url} ...")
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                path = Path(ydl.prepare_filename(info)).with_suffix(".mp4")
        except Exception as e:  # noqa: BLE001
            msg = re.sub(r"\x1b\[[0-9;]*m", "", str(e))
            hint = "" if args.cookies_from else "\n  If it needs a login, try again with --cookies-from chrome"
            print(f"  !! failed: {msg}{hint}")
            continue
        if not path.exists():
            found = sorted(dest.glob(f"{info.get('extractor', '*')}-{info.get('id')}.*"))
            path = found[0] if found else die(f"downloaded file not found for {url}")
        meta = {k: info.get(k) for k in ("webpage_url", "title", "uploader", "duration", "description", "upload_date")}
        path.with_suffix(".json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  saved {path.relative_to(REPO)}  ({info.get('title', '')[:60]})")
        if not args.no_analyze:
            subprocess.run([sys.executable, str(Path(__file__).with_name("analyze.py")), str(path), "--project", args.project])


if __name__ == "__main__":
    main()
