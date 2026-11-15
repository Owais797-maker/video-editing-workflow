#!/usr/bin/env python3
"""Save the editing style of a reference video so every future video can use it.

    python tools/save_style.py reels-bold --project my-reel --reference "inspo.mp4" --default

Creates styles/<name>/:
    style.json   defaults applied to every edit.json that uses this style (fill/adjust it!)
    style.md     description of the style in words (pacing, captions, look, music ...)
    sheet.jpg    contact sheet of the reference, to remember what it looked like
    pacing.json  measured shot lengths of the reference

With --default the style becomes the default for all new edits (styles/default.txt).
Existing style.json/style.md are never overwritten; use it again to refresh sheet/pacing.
"""
import argparse
import json
import shutil

from common import EDITS, REPO, die, file_key, load_json, resolve, save_json
from edl import STYLES

TEMPLATE = {
    "output": {"width": 1080, "height": 1920, "fps": 30, "fit": "crop"},
    "transition": {"type": "cut"},
    "motion": {"type": "zoom_in", "amount": 0.08},
    "captions": {"words_per_line": 3,
                 "style": {"font": "Poppins ExtraBold", "bold": False, "size": 4.8, "color": "white",
                           "highlight_color": "#FFE600", "highlight_scale": 1.1, "uppercase": True,
                           "animation": "pop", "position": "bottom", "margin": 22}},
    "text": {"font": "Bebas Neue", "size": 7, "animation": "pop", "color": "white"},
    "lower_third": {"font": "Montserrat", "color": "#E91E63"},
    "overlay": {"animation": "pop", "width": 0.18},
    "look": {"contrast": 1.05, "saturation": 1.1},
    "music": {"volume": 0.2, "duck": True},
    "loudness": -14,
}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("name", help="style name, e.g. reels-bold")
    ap.add_argument("--project", required=True)
    ap.add_argument("--reference", required=True, help="reference video (file name in Reference/<project>/ or path)")
    ap.add_argument("--default", action="store_true", help="make this the default style")
    args = ap.parse_args()

    ref = EDITS / "Reference" / args.project / args.reference
    ref = ref if ref.exists() else resolve(args.reference)
    adir = EDITS / "Export" / args.project / "work" / "analysis" / file_key(ref)
    if not (adir / "analysis.json").exists():
        die(f"no analysis for {ref.name}. Run: python tools/analyze.py \"{ref.relative_to(REPO).as_posix()}\" --project {args.project}")
    an = load_json(adir / "analysis.json")

    sdir = STYLES / args.name
    sdir.mkdir(parents=True, exist_ok=True)
    shutil.copy(adir / "sheet.jpg", sdir / "sheet.jpg")
    info, stats = an["info"], an["stats"]
    save_json(sdir / "pacing.json", {"reference": ref.name, "stats": stats,
                                     "shot_lengths": [s["length"] for s in an["shots"]]})
    if not (sdir / "style.json").exists():
        st = json.loads(json.dumps(TEMPLATE))
        w, h = info["width"], info["height"]
        if w > h:
            st["output"].update(width=1920, height=1080)
        elif w == h:
            st["output"].update(width=1080, height=1080)
        save_json(sdir / "style.json", st)
    if not (sdir / "style.md").exists():
        (sdir / "style.md").write_text(
            f"# Style: {args.name}\n\nLearned from `{ref.name}` (project `{args.project}`).\n\n"
            "![reference](sheet.jpg)\n\n"
            f"- **Pacing:** {stats['shots']} shots, average {stats['avg_shot']}s "
            f"(median {stats['median_shot']}s), {stats['cuts_per_minute']} cuts/min\n"
            "- **Hook (first 2 s):** TODO\n- **Captions:** TODO (font feel, size, position, colour, words per line, highlight)\n"
            "- **On-screen titles:** TODO\n- **Transitions / motion:** TODO\n- **Look / colour:** TODO\n"
            "- **Music / sound:** TODO\n- **Ending:** TODO\n- **Owner's notes:** TODO\n", encoding="utf-8")
    if args.default:
        (STYLES / "default.txt").write_text(args.name + "\n", encoding="utf-8")
    print(f"Style saved: {sdir.relative_to(REPO)}/  (edit style.json and style.md to match the reference)")
    if args.default:
        print(f"'{args.name}' is now the default style.")


if __name__ == "__main__":
    main()
