#!/usr/bin/env python3
"""Build captions for the final video from the Whisper transcripts of its shots.

    python tools/captions.py "Video Edits/Export/my-reel/edit.json"

Takes the words spoken inside each shot's in/out range, moves them onto the
final video's timeline (speed and transitions included), groups them into short
lines, and writes Export/<project>/captions.json.

captions.json is plain text you can correct by hand (spelling, Urdu script,
line breaks) before rendering. It is NOT regenerated automatically, so your
corrections stay; run this again with --force to rebuild it from scratch.
"""
import argparse
import re

import edl
from common import REPO, die, file_key, load_json, resolve, save_json

PUNCT = re.compile(r"[.!?،۔؟,;:]$")


def collect_words(edit: dict) -> list[dict]:
    tdir = edit["_dir"] / "work" / "transcripts"
    words = []
    for s in edit["shots"]:
        if s.get("mute") or s.get("no_captions") or not s["_info"]["has_audio"]:
            continue
        tfile = tdir / f"{file_key(s['_src'])}.json"
        if not tfile.exists():
            die(f"no transcript for {s['src']}. Run:\n  python tools/transcribe.py \"{s['_src'].relative_to(REPO).as_posix()}\" --project {edit['project']}")
        for seg in load_json(tfile)["segments"]:
            for w in seg["words"]:
                mid = (w["start"] + w["end"]) / 2
                if s["in"] <= mid < s["out"]:
                    a = s["_start"] + (max(w["start"], s["in"]) - s["in"]) / s["speed"]
                    b = s["_start"] + (min(w["end"], s["out"]) - s["in"]) / s["speed"]
                    words.append({"start": round(a, 3), "end": round(max(b, a + 0.05), 3), "text": w["text"], "shot": s["_n"]})
    words.sort(key=lambda w: w["start"])
    return words


def group(words: list[dict], per_line: int, max_gap: float) -> list[dict]:
    lines, cur = [], []
    for w in words:
        if cur and (len(cur) >= per_line or w["start"] - cur[-1]["end"] > max_gap
                    or w["shot"] != cur[-1]["shot"] or PUNCT.search(cur[-1]["text"])):
            lines.append(cur)
            cur = []
        cur.append(w)
    if cur:
        lines.append(cur)
    out = []
    for i, ws in enumerate(lines):
        end = ws[-1]["end"] + 0.25
        if i + 1 < len(lines):
            end = min(end, lines[i + 1][0]["start"])
        out.append({"start": ws[0]["start"], "end": round(end, 3),
                    "text": " ".join(w["text"] for w in ws),
                    "words": [{k: w[k] for k in ("start", "end", "text")} for w in ws]})
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("edit")
    ap.add_argument("--force", action="store_true", help="overwrite an existing captions.json")
    args = ap.parse_args()

    edit = edl.load(resolve(args.edit))
    cfg = edit.get("captions") or die("edit.json has no \"captions\" section")
    dest = edit["_dir"] / cfg.get("file", "captions.json")
    if dest.exists() and not args.force:
        die(f"{dest.relative_to(REPO)} already exists (it may contain your corrections). Use --force to rebuild it.")
    lines = group(collect_words(edit), int(cfg.get("words_per_line", 3)), float(cfg.get("max_gap", 0.6)))
    save_json(dest, {"note": "Edit 'text' and the words freely; times are seconds on the final video.", "lines": lines})
    print(f"{len(lines)} caption lines -> {dest.relative_to(REPO)}")


if __name__ == "__main__":
    main()
