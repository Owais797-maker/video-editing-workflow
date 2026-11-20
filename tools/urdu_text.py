#!/usr/bin/env python3
"""Big Urdu-script titles as transparent PNGs (right-to-left, proper Nastaliq shaping via Chromium),
for the owner's TikTok hooks ("جانوروں کا وزن تیزی سے بڑھانے والا ...").

    python tools/urdu_text.py --project my-reel --name hook \
        --line "جانوروں کا وزن:nastaliq" --line "تیزی سے بڑھانے والا:bold-yellow" --line "BUTTER FAT MILK:latin"

Each --line is "text:preset". Presets (see guides/urdu-typography.md):
  noori / noori-gold / noori-red   Jameel Noori Nastaleeq (owner's font, real Noori look)
  mehr            Mehr Nastaliq (ITU), elegant Nastaliq
  aslam           Aslam display Urdu
  mushaf          Al Mushaf (Arabic / Quranic naskh: Arabic text only)
  nastaliq        Noori-style Nastaliq (Gulzar), white, soft dark shadow  - the classic
  nastaliq-gold   same, gold #FFD400 with a thin dark stroke
  nastaliq-red    same, red #FF2A2A with a white stroke (like the owner's 114k hit)
  bold            Lalezar heavy display, white with a black stroke  - loud, poster-like
  bold-yellow     Lalezar, yellow with a black stroke
  bold-red        Lalezar, red with a white stroke
  ruqaa           Aref Ruqaa calligraphy, gold  - one elegant word
  kufi            Reem Kufi modern geometric, white  - short words only (its ے looks odd in long Urdu)
  naskh           Noto Naskh Arabic Bold, white  - very readable small lines
  latin           Montserrat Black caps, white  - for English product names inside an Urdu stack
Options: --size (px at 1080 wide, default 96), --scale per line "text:preset:1.3", --width (0-1, default 0.86).
Writes Video Edits/Raw/<project>/urdu-<name>.png (2160 px canvas width, trimmed). Use it as an overlay
(x/y/width, animation pop/slide_up) on frame 1, fully visible at 0.0 s.
"""
import argparse
import html
import json
import subprocess
from pathlib import Path

from common import EDITS, FONTS, die

HERE = Path(__file__).resolve().parent
FONT_FILES = [("Gulzar", "Gulzar-400", 400), ("Jameel Noori Nastaleeq", "JameelNooriNastaleeq-400", 400),
              ("Mehr Nastaliq", "MehrNastaliq-400", 400), ("Aslam", "Aslam-400", 400), ("Al Mushaf", "AlMushaf-400", 400), ("Noto Nastaliq Urdu", "NotoNastaliqUrdu-700", 700),
              ("Lalezar", "Lalezar-400", 400), ("Aref Ruqaa", "ArefRuqaa-700", 700), ("Reem Kufi", "ReemKufi-700", 700),
              ("Noto Naskh Arabic", "NotoNaskhArabic-700", 700), ("Montserrat Black", "Montserrat-900", 400)]
PRESETS = {
    "nastaliq": dict(font="Gulzar", color="#FFFFFF", stroke=0, stroke_color="#000", shadow=True, lh=1.55, k=1.15),
    "nastaliq-gold": dict(font="Gulzar", color="#FFD400", stroke=5, stroke_color="#1a1200", shadow=True, lh=1.55, k=1.15),
    "nastaliq-red": dict(font="Gulzar", color="#FF2A2A", stroke=7, stroke_color="#FFFFFF", shadow=True, lh=1.55, k=1.15),
    "noori": dict(font="Jameel Noori Nastaleeq", color="#FFFFFF", stroke=0, stroke_color="#000", shadow=True, lh=1.7, k=1.25),
    "noori-gold": dict(font="Jameel Noori Nastaleeq", color="#FFD400", stroke=5, stroke_color="#1a1200", shadow=True, lh=1.7, k=1.25),
    "noori-red": dict(font="Jameel Noori Nastaleeq", color="#FF2A2A", stroke=7, stroke_color="#FFFFFF", shadow=True, lh=1.7, k=1.25),
    "mehr": dict(font="Mehr Nastaliq", color="#FFFFFF", stroke=0, stroke_color="#000", shadow=True, lh=1.8, k=1.15),
    "aslam": dict(font="Aslam", color="#FFFFFF", stroke=0, stroke_color="#000", shadow=True, lh=1.5, k=1.2),
    "mushaf": dict(font="Al Mushaf", color="#FFFFFF", stroke=0, stroke_color="#000", shadow=True, lh=1.6, k=1.1),
    "bold": dict(font="Lalezar", color="#FFFFFF", stroke=9, stroke_color="#000000", shadow=True, lh=1.25, k=1.05),
    "bold-yellow": dict(font="Lalezar", color="#FFD400", stroke=9, stroke_color="#000000", shadow=True, lh=1.25, k=1.05),
    "bold-red": dict(font="Lalezar", color="#FF2A2A", stroke=9, stroke_color="#FFFFFF", shadow=True, lh=1.25, k=1.05),
    "ruqaa": dict(font="Aref Ruqaa", color="#FFD27A", stroke=0, stroke_color="#000", shadow=True, lh=1.35, k=1.1),
    "kufi": dict(font="Reem Kufi", color="#FFFFFF", stroke=0, stroke_color="#000", shadow=True, lh=1.3, k=0.95),
    "naskh": dict(font="Noto Naskh Arabic", color="#FFFFFF", stroke=0, stroke_color="#000", shadow=True, lh=1.45, k=0.8),
    "latin": dict(font="Montserrat Black", color="#FFFFFF", stroke=0, stroke_color="#000", shadow=True, lh=1.05, k=0.8, ltr=True),
}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--line", action="append", required=True, help='"text:preset[:scale]"')
    ap.add_argument("--size", type=float, default=96)
    ap.add_argument("--width", type=float, default=0.86)
    ap.add_argument("--plate", default="", help="backing behind each line: dark | black | red | blue | yellow | #RRGGBB (default none)")
    args = ap.parse_args()
    fonts = []
    for fam, stem, w in FONT_FILES:
        hit = next(FONTS.rglob(stem + ".ttf"), None)
        if not hit:
            die(f"font {stem} missing: python3 tools/get_fonts.py '{fam}:{w}' --folder 'Urdu Fonts'")
        fonts.append({"family": fam, "path": str(hit), "weight": w, "style": "normal"})
    rows = []
    for spec in args.line:
        parts = spec.rsplit(":", 2)
        if len(parts) == 3 and parts[2].replace(".", "", 1).isdigit():
            text, preset, sc = parts[0], parts[1], float(parts[2])
        else:
            text, preset = spec.rsplit(":", 1)
            sc = 1.0
        p = PRESETS.get(preset) or die(f"unknown preset {preset}: {', '.join(PRESETS)}")
        size = args.size * p["k"] * sc
        stroke = f"-webkit-text-stroke:{p['stroke']}px {p['stroke_color']};paint-order:stroke fill;" if p["stroke"] else ""
        shadow = "text-shadow:0 6px 18px rgba(0,0,0,.55),0 2px 3px rgba(0,0,0,.5);" if p["shadow"] else ""
        plate = {"dark": "rgba(0,0,0,.62)", "black": "#000", "red": "#E3121B", "blue": "#1E3FA0", "yellow": "#FFD400"}.get(args.plate, args.plate)
        box = (f"background:{plate};padding:.02em .45em .12em;border-radius:.22em;box-shadow:0 10px 30px rgba(0,0,0,.35);"
               if plate else "")
        rows.append(f'<div dir="{"ltr" if p.get("ltr") else "rtl"}" style="white-space:nowrap;font-family:\'{p["font"]}\';font-size:{size:.0f}px;'
                    f'line-height:{p["lh"]};color:{p["color"]};{stroke}{shadow}{box}">{html.escape(text)}</div>')
    W = 1080
    css = (f"#cap{{position:absolute;left:{(1 - args.width) / 2 * 100:.1f}%;right:{(1 - args.width) / 2 * 100:.1f}%;top:40px;"
           "display:flex;flex-direction:column;align-items:center;text-align:center;gap:6px;}")
    out = EDITS / "Raw" / args.project / f"urdu-{args.name}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    work = EDITS / "Export" / args.project / "work" / "urdu"
    work.mkdir(parents=True, exist_ok=True)
    raw = work / f"{args.name}-full.png"
    job = work / f"{args.name}.json"
    job.write_text(json.dumps({"width": W, "height": 1920, "scale": 2, "css": css, "fonts": fonts,
                               "states": [{"file": str(raw), "html": "".join(rows)}]}), encoding="utf-8")
    subprocess.run(["node", str(HERE / "htmlcaps" / "render.js"), str(job)], check=True, capture_output=True)
    from PIL import Image
    im = Image.open(raw)
    bb = im.getbbox() or (0, 0, im.width, im.height)
    pad = 24
    im.crop((max(0, bb[0] - pad), max(0, bb[1] - pad), min(im.width, bb[2] + pad), min(im.height, bb[3] + pad))).save(out)
    print(f"Urdu title: {out}  ({im.width}px canvas, trimmed)")


if __name__ == "__main__":
    main()
