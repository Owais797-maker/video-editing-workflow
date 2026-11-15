#!/usr/bin/env python3
"""Sync captions with the owner's Caption Review page (an artifact with a small database).

    python tools/caption_review.py push "Video Edits/Export/my-reel/edit.json" [--note 6="unclear word"]
        -> writes work/review/batch.json: the writes for ArtifactData action "batch"
           (project doc + one doc per caption line), to send with file_path entries

    python tools/caption_review.py pull "Video Edits/Export/my-reel/edit.json" <dir>
        -> <dir> is the out_dir of an ArtifactData "list" of projects/<project>/lines;
           writes the owner's wording into captions.txt and applies it (exact timing kept
           when the word count matches, see caption_text.py)

Review page: https://claude.ai/artifact/WNJDd3kh3petc3Hgc3cXY5
Database layout: projects/<project> {title, status, updated}; projects/<project>/lines/<001>
{n, start, text, note?, edited?}. Text uses the caption_text.py marks (*big*, _ hidden).
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import edl
from common import REPO, die, load_json, resolve

URL = "https://claude.ai/artifact/WNJDd3kh3petc3Hgc3cXY5"


def rows(lines: list) -> list:
    return [" ".join(f"*{w['text']}*" if w.get("big") else w["text"] for w in ln.get("words") or []) or ln["text"]
            for ln in lines]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=["push", "pull"])
    ap.add_argument("edit")
    ap.add_argument("dir", nargs="?")
    ap.add_argument("--note", action="append", default=[], help='N="text" note shown under line N')
    args = ap.parse_args()
    edit = edl.load(resolve(args.edit))
    if not edit.get("captions"):
        die("edit.json has no captions")
    cfile = edit["_dir"] / edit["captions"].get("file", "captions.json")
    lines = load_json(cfile)["lines"]
    project = edit["project"]
    work = edit["_dir"] / "work" / "review"
    work.mkdir(parents=True, exist_ok=True)

    if args.action == "push":
        notes = {}
        for n in args.note:
            k, _, v = n.partition("=")
            notes[int(k)] = v.strip('"')
        writes = [{"op": "set", "collection": "projects", "doc_id": project,
                   "data": {"title": edit.get("title", project), "status": "review",
                            "updated": datetime.now(timezone.utc).isoformat(), "count": len(lines)}}]
        for i, (ln, text) in enumerate(zip(lines, rows(lines)), 1):
            d = {"n": i, "start": round(ln["start"], 2), "text": text, "edited": False}
            if i in notes:
                d["note"] = notes[i]
            writes.append({"op": "set", "collection": f"projects/{project}/lines", "doc_id": f"{i:03d}", "data": d})
        out = work / "batch.json"
        out.write_text(json.dumps(writes, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{len(writes)} writes -> {out.relative_to(REPO)}  (send with ArtifactData batch; existing docs need if_version)")
        return

    if not args.dir:
        die("pull needs the directory the lines were saved to")
    src = Path(args.dir)
    files = sorted(src.rglob("*.json"))
    if not files:
        die(f"no line files under {src}")
    got = {}
    for f in files:
        d = json.loads(f.read_text(encoding="utf-8"))
        d = d.get("data", d)
        if "n" in d:
            got[int(d["n"])] = d.get("text", "")
    if len(got) != len(lines):
        die(f"review has {len(got)} lines but captions.json has {len(lines)}; push again first")
    tfile = cfile.with_suffix(".txt")
    tfile.write_text("\n".join(f"{n} | {got[n]}" for n in sorted(got)) + "\n", encoding="utf-8")
    print(f"owner's wording -> {tfile.relative_to(REPO)}")
    subprocess.run([sys.executable, str(Path(__file__).with_name("caption_text.py")), "apply", args.edit], check=True)


if __name__ == "__main__":
    main()
