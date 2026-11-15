#!/usr/bin/env python3
"""Edit caption wording as plain text: correct mistakes, or rewrite it in Roman Urdu
or English, while keeping the timing.

    python tools/caption_text.py export "Video Edits/Export/my-reel/edit.json"
        -> writes captions.txt, one numbered caption line per row:
           1 | یہ میرا پہلا
           2 | ولاگ ہے

    (edit captions.txt: e.g. "1 | yeh mera pehla" / "2 | vlog hai")

    python tools/caption_text.py apply "Video Edits/Export/my-reel/edit.json"
        -> puts the new words back into captions.json

Keep the line numbers. If a line keeps the same number of words, each word keeps its
exact timing (best for word highlighting); otherwise the line's time is shared out
across the new words by length.
"""
import argparse
import re

import edl
from common import REPO, die, load_json, resolve, save_json

ROW = re.compile(r"^\s*(\d+)\s*\|\s?(.*)$")


def respread(line: dict, words: list[str]) -> list[dict]:
    old = line.get("words") or []
    if len(old) == len(words):
        return [{**o, "text": w} for o, w in zip(old, words)]
    a, b = line["start"], (old[-1]["end"] if old else line["end"])
    weights = [len(w) + 2 for w in words]
    total, t, out = sum(weights), a, []
    for w, k in zip(words, weights):
        d = (b - a) * k / total
        out.append({"start": round(t, 3), "end": round(t + d, 3), "text": w})
        t += d
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=["export", "apply"])
    ap.add_argument("edit")
    args = ap.parse_args()
    edit = edl.load(resolve(args.edit))
    if not edit.get("captions"):
        die("edit.json has no \"captions\" section")
    cfile = edit["_dir"] / edit["captions"].get("file", "captions.json")
    tfile = cfile.with_suffix(".txt")
    data = load_json(cfile)
    lines = data["lines"]

    if args.action == "export":
        tfile.write_text("\n".join(f"{i} | {ln['text']}" for i, ln in enumerate(lines, 1)) + "\n", encoding="utf-8")
        print(f"{len(lines)} lines -> {tfile.relative_to(REPO)}")
        return

    if not tfile.exists():
        die(f"{tfile.relative_to(REPO)} not found; run 'export' first")
    new = {}
    for row in tfile.read_text(encoding="utf-8").splitlines():
        if not row.strip():
            continue
        m = ROW.match(row) or die(f"bad row (expected 'number | text'): {row}")
        new[int(m.group(1))] = m.group(2).strip()
    unknown = sorted(set(new) - set(range(1, len(lines) + 1)))
    if unknown:
        die(f"captions.txt has line numbers that don't exist: {unknown}")
    kept = []
    for i, ln in enumerate(lines, 1):
        text = new.get(i, ln["text"])
        if not text:  # empty row = drop this caption
            continue
        ln["words"] = respread(ln, text.split())
        ln["text"] = " ".join(w["text"] for w in ln["words"])
        kept.append(ln)
    data["lines"] = kept
    save_json(cfile, data)
    print(f"{len(kept)} lines updated in {cfile.relative_to(REPO)}")


if __name__ == "__main__":
    main()
