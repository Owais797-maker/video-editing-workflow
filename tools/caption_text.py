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

Mark the word to show BIG in kinetic captions with stars: "is ki *zaroorat*". A lone "_" is a
silent placeholder: it keeps a spoken word's time slot but shows nothing.
Keep the line numbers; an empty row drops that caption. If the kept rows have the same
total number of words as before, lines can be re-broken freely (move words between
rows) and every word keeps its exact spoken time. Otherwise each row keeps its own time
span, shared out across its new words by length.
"""
import argparse
import re

import edl
from common import REPO, die, load_json, resolve, save_json

ROW = re.compile(r"^\s*(\d+)\s*\|\s?(.*)$")


def mark(w: dict) -> dict:
    """*word* = show this word big (kinetic captions). _ = silent placeholder (keeps timing, not shown)."""
    w = {k: v for k, v in w.items() if k != "big"}
    t = w["text"]
    if len(t) > 2 and t.startswith("*") and t.endswith("*"):
        w["text"], w["big"] = t[1:-1], True
    return w


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
        rows = [" ".join(f"*{w['text']}*" if w.get("big") else w["text"] for w in ln.get("words") or []) or ln["text"]
                for ln in lines]
        tfile.write_text("\n".join(f"{i} | {r}" for i, r in enumerate(rows, 1)) + "\n", encoding="utf-8")
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
    texts = {i: new.get(i, ln["text"]) for i, ln in enumerate(lines, 1)}
    keep_ids = [i for i in texts if texts[i]]  # empty row = drop this caption
    # pool: words of every caption not explicitly emptied (rows left out of the file still count,
    # so the file may re-break the words into fewer or more rows)
    pool = [w for i, ln in enumerate(lines, 1) if not (i in new and not new[i]) for w in (ln.get("words") or [])]
    rows_given = [new[i] for i in sorted(new) if new[i]]
    if pool and sum(len(t.split()) for t in rows_given) == len(pool):
        keep_ids = None
        new_words = [t.split() for t in rows_given]
    else:
        new_words = [t.split() for t in (texts[i] for i in keep_ids)]
        pool = [w for i in keep_ids for w in (lines[i - 1].get("words") or [])]
    if pool and sum(map(len, new_words)) == len(pool):
        # same number of words overall: lines may be re-broken freely, each word keeps its exact time
        k = 0
        for ws in new_words:
            seg = pool[k:k + len(ws)]
            k += len(ws)
            kept.append({"start": seg[0]["start"], "end": seg[-1]["end"] + 0.25,
                         "words": [mark({**w, "text": t}) for w, t in zip(seg, ws)],
                         "text": " ".join(t.strip("*") for t in ws)})
        for a, b in zip(kept, kept[1:]):
            a["end"] = round(min(a["end"], b["start"]), 3)
        print("word timing: exact (lines re-broken)")
    else:
        for i in keep_ids:
            ln = lines[i - 1]
            ln["words"] = [mark(w) for w in respread(ln, texts[i].split())]
            ln["text"] = " ".join(w["text"] for w in ln["words"])
            kept.append(ln)
    data["lines"] = kept
    save_json(cfile, data)
    print(f"{len(kept)} lines updated in {cfile.relative_to(REPO)}")


if __name__ == "__main__":
    main()
