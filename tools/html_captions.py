#!/usr/bin/env python3
"""HTML/CSS caption engine: designer-grade animated captions rendered with headless Chromium.

Used by render.py when captions.style.mode == "html":
    "captions": {"style": {"mode": "html", "template": "editorial", "accent": "#FFD400", "y": 0.68,
                           "layout": "stack" | "flow"}}
Templates live in tools/htmlcaps/templates.css: box-pop, editorial, minimal, outline-3d, press, glass.
Each word pops in exactly when it is spoken (4-frame eased entrance), using the word timings
in captions.json and the *big* marks from caption_text.py.

    python tools/html_captions.py --showcase "Video Edits/Export/p/edit.json" --at 12.4
        -> one frame of the video with a sample line in every template (to choose a look)
"""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
from pathlib import Path

from common import FONTS, REPO, die, load_json, need, resolve, run

HERE = Path(__file__).resolve().parent / "htmlcaps"
TEMPLATES = ["box-pop", "editorial", "minimal", "outline-3d", "press", "glass", "swiss", "explainer", "script-mix", "pill"]
STACKED = {"editorial", "press"}  # templates that put the big word on its own row
ENTRANCE = [0.0, 0.62, 1.12, 1.0]  # eased progress per frame (overshoot, settle)
ENTRANCE_BY_TPL = {"script-mix": [i / 9 for i in range(10)]}  # letters type in over ~0.3 s
FONT_FILES = [  # (css family, file stem, weight, style)
    ("Montserrat Black", "Montserrat-900", 400, "normal"),
    ("Poppins SemiBold", "Poppins-600", 400, "normal"),
    ("Instrument Serif", "InstrumentSerif-400i", 400, "italic"),
    ("Instrument Serif", "InstrumentSerif-400", 400, "normal"),
    ("Anton", "Anton-400", 400, "normal"),
    ("Oswald", "Oswald-700", 700, "normal"),
    ("Inter Tight", "InterTight-800", 800, "normal"),
    ("Inter Tight", "InterTight-900", 900, "normal"),
    ("Bebas Neue", "BebasNeue-400", 400, "normal"),
    ("Playfair Display", "PlayfairDisplay-800i", 800, "italic"),
    ("Yellowtail", "Yellowtail-400", 400, "normal"),
]


def fonts() -> list:
    out = []
    for fam, stem, w, st in FONT_FILES:
        hit = next(FONTS.rglob(stem + ".ttf"), None)
        if hit:
            out.append({"family": fam, "path": str(hit), "weight": w, "style": st})
    return out


def line_html(words: list, k: int, p: float, kw: set, pick, layout: str) -> str:
    """HTML for one moment: words[0..k-1] past, words[k] active at progress p, the rest future."""
    def span(i: int) -> str:
        w = words[i]
        if w["text"] == "_":
            return ""
        cls = ["w", "past" if i < k else "active" if i == k else "future"]
        key = re.sub(r"[^\w]", "", w["text"].lower())
        if i == pick:
            cls.append("big")
        elif key in kw:
            cls.append("kw")
        else:
            cls.append("small")
        style = f' style="--p:{p:.3f}"' if i == k else ""
        return f'<span class="{" ".join(cls)}"{style}>{html.escape(w["text"])}</span>'

    idx = list(range(len(words)))
    if layout == "column":  # every word on its own row (Swiss top captions)
        groups = [[i] for i in idx]
    elif layout == "stack" and pick is not None:
        groups = [[i for i in idx if i < pick], [pick], [i for i in idx if i > pick]]
    else:
        groups = [idx]
    rows = ["".join(span(i) for i in g) for g in groups if g]
    return "".join(f'<div class="row">{r}</div>' for r in rows if r)


def build(edit: dict, cap: dict, lines: list, plan: list, out_dir: Path, fps: int, total: float) -> Path:
    """Render the caption layer; returns an ffconcat file (full-frame transparent PNGs with durations)."""
    need("node")
    st = cap.get("style", {})
    tpl = st.get("template", "editorial")
    if tpl not in TEMPLATES:
        die(f"caption template must be one of {TEMPLATES}")
    layout = st.get("layout", "column" if tpl == "swiss" else "stack" if tpl in STACKED else "flow")
    accent = st.get("accent", st.get("highlight_color", "#FFD400"))
    lower = st.get("lowercase", tpl in ("editorial", "minimal", "glass", "swiss"))
    upper_kw = {k.lower() for k in (cap.get("keywords") or {})}
    W, H = edit["output"]["width"], edit["output"]["height"]
    shutil.rmtree(out_dir, ignore_errors=True)
    out_dir.mkdir(parents=True)
    css = (HERE / "templates.css").read_text(encoding="utf-8")
    y = float(st.get("y", 0.17 if tpl == "swiss" else 0.68))
    safe = edit.get("safe") or {}
    if safe:  # keep captions inside the TikTok / Reels / Status safe zone
        y = min(max(y, float(safe.get("top", 0)) + 0.05), 1 - float(safe.get("bottom", 0)) - 0.04)
        css += (f"\n#cap{{left:{float(safe.get('left', .06)) * 100:.1f}%;"
                f"right:{float(safe.get('right', .06)) * 100:.1f}%;}}")
    css += f"\n#cap{{--accent:{accent};--y:{y};--ink:{st.get('ink', '#111')};--pill:{st.get('pill', '#1E3FA0')};}}"
    if layout == "column":  # stacked words grow downward from y (keeps the first word in the safe zone)
        css += "\n#cap{transform:none;}"
    scale = H / 1920
    if scale != 1:
        css += f"\n#cap{{zoom:{scale:.4f};}}"
    states, timeline = [], []  # timeline: (start, end, file or None)
    fdur = 1.0 / fps
    n = 0
    for ln, pick in zip(lines, plan):
        words = [dict(w, text=(w["text"].lower() if lower and re.sub(r"[^\w]", "", w["text"].lower()) not in upper_kw else w["text"]))
                 for w in (ln.get("words") or [])]
        if not words or all(w["text"] == "_" for w in words):
            continue
        for k, w in enumerate(words):
            a = w["start"] if k else ln["start"]
            b = words[k + 1]["start"] if k + 1 < len(words) else ln["end"]
            if b - a < fdur / 2:
                continue
            t = a
            frames = ENTRANCE_BY_TPL.get(tpl, ENTRANCE) if w["text"] != "_" else [1.0]
            for j, p in enumerate(frames):
                last = j == len(frames) - 1 or t + fdur >= b
                end = b if last else t + fdur
                file = out_dir / f"c{n:05d}.png"
                n += 1
                body = line_html(words, k, p, upper_kw, pick, layout)
                if ln.get("y") is not None:  # per-line position (e.g. move off a face): shift from the style's y
                    body = f'<div style="position:relative;top:{(float(ln["y"]) - y) * 1920:.0f}px">{body}</div>'
                states.append({"file": str(file), "html": body})
                timeline.append((t, end, file))
                t = end
                if last:
                    break
    for s_ in states:
        s_["html"] = f'<div class="t-{tpl}" style="display:contents">{s_["html"]}</div>'
    job = out_dir / "job.json"
    job.write_text(json.dumps({"width": W, "height": H, "css": css, "fonts": fonts(), "states": states}), encoding="utf-8")
    run(["node", str(HERE / "render.js"), str(job)])
    blank = out_dir / "blank.png"
    from PIL import Image
    Image.new("RGBA", (W, H), (0, 0, 0, 0)).save(blank)
    # ffconcat with gaps filled by the blank frame
    entries, t = [], 0.0
    for a, b, f in sorted(timeline, key=lambda x: x[0]):
        if a > t + 1e-3:
            entries.append((blank, a - t))
        entries.append((f, max(b - max(a, t), fdur / 2)))
        t = max(t, b)
    if t < total:
        entries.append((blank, total - t))
    lst = out_dir / "captions.ffconcat"
    body = ["ffconcat version 1.0"]
    for f, d in entries:
        body += [f"file '{Path(f).name}'", f"duration {d:.4f}"]
    body.append(f"file '{Path(entries[-1][0]).name}'")
    lst.write_text("\n".join(body) + "\n", encoding="utf-8")
    return lst


def showcase(edit_path: str, at: float, line_no: int | None) -> None:
    import edl
    import render
    edit = edl.load(resolve(edit_path))
    cap = edit.get("captions") or {}
    lines = load_json(edit["_dir"] / cap.get("file", "captions.json"))["lines"]
    plan = render.plan_kinetic(lines, cap)
    i = line_no - 1 if line_no else max(range(len(lines)), key=lambda j: (plan[j] is not None, len(lines[j]["words"])))
    ln, pick = lines[i], plan[i]
    out = edit["_dir"] / "work" / "showcase"
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    frame = out / "frame.png"
    shot = next((sh for sh in edit["shots"] if sh["_start"] <= at < sh["_start"] + sh["_len"]), edit["shots"][0])
    src_t = shot["in"] + (at - shot["_start"]) * shot["speed"]
    run(["ffmpeg", "-y", "-v", "error", "-ss", f"{src_t:.3f}", "-i", str(shot["_src"]), "-frames:v", "1",
         "-filter_complex", edl.fit_filter(edit, shot, "[0:v]", "[o]"), "-map", "[o]", str(frame)])
    W, H = edit["output"]["width"], edit["output"]["height"]
    accent = cap.get("style", {}).get("accent", "#FFD400")
    kw = {k.lower() for k in (cap.get("keywords") or {})}
    states = []
    css = (HERE / "templates.css").read_text(encoding="utf-8") + f"\n#cap{{--accent:{accent};--y:.62;}}"
    for tpl in TEMPLATES:
        words = [dict(w, text=w["text"].lower() if tpl in ("editorial", "minimal", "glass") and
                      re.sub(r"[^\w]", "", w["text"].lower()) not in kw else w["text"]) for w in ln["words"]]
        k = len(words) - 1
        lay = "stack" if tpl in STACKED else "flow"
        states.append({"file": str(out / f"{tpl}.png"),
                       "html": f'<div class="t-{tpl}" style="display:contents">{line_html(words, k, 1.0, kw, pick, lay)}</div>'})
    job = out / "job.json"
    job.write_text(json.dumps({"width": W, "height": H, "css": css, "fonts": fonts(), "states": states}), encoding="utf-8")
    run(["node", str(HERE / "render.js"), str(job)])
    from PIL import Image, ImageDraw, ImageFont
    base = Image.open(frame).convert("RGBA")
    tiles = []
    lab = ImageFont.truetype(str(next(FONTS.rglob("Poppins-600.ttf"))), 44)
    for n, tpl in enumerate(TEMPLATES, 1):
        im = base.copy()
        im.alpha_composite(Image.open(out / f"{tpl}.png"))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((30, 30, 30 + 70 + d.textlength(tpl, font=lab), 100), 20, fill=(0, 0, 0, 170))
        d.text((50, 38), f"{n} {tpl}", font=lab, fill=(255, 255, 255, 255))
        tiles.append(im.convert("RGB").resize((W // 2, H // 2)))
    sheet = Image.new("RGB", (tiles[0].width * 3 + 20, tiles[0].height * 2 + 10), (0, 0, 0))
    for n, t in enumerate(tiles):
        sheet.paste(t, ((n % 3) * (t.width + 10), (n // 3) * (t.height + 10)))
    dest = out / "templates.jpg"
    sheet.save(dest, quality=88)
    print(f"Showcase: {dest.relative_to(REPO)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--showcase", metavar="EDIT_JSON", required=True)
    ap.add_argument("--at", type=float, default=10.0, help="time of the video frame to use")
    ap.add_argument("--line", type=int, help="caption line number to show (default: a line with a big word)")
    a = ap.parse_args()
    showcase(a.showcase, a.at, a.line)
