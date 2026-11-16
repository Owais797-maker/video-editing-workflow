"""Brand cards: full-frame motion-graphic inserts rendered with HTML/CSS (style learned from the
Buttery Milk reel). The voice keeps playing underneath; the card covers the picture.

In edit.json:
  "brand": {"bg1": "#1E8C3A", "bg2": "#0A3A17", "accent": "#F5C518", "ink": "#111111"},
  "cards": [
    {"type": "headline", "start": 5.0, "end": 7.2, "label": "Buttery Milk",
     "title": "Trusted\\nfor *years*", "product": "bag-cutout.png"},
    {"type": "stats", "start": 15, "end": 18, "label": "Buttery Milk", "align": "left",
     "stats": [{"value": "26–28%", "tag": "Butter fat"}, {"value": "34%", "tag": "Protein"}],
     "product": "bag-cutout.png", "product_size": 0.24, "product_pos": "bottom-right"},
    {"type": "contact", "start": 22, "end": 26, "title": "Khyber *Traders*",
     "lines": ["Wholesale orders"], "phones": ["0335 2999006"], "small": "@animalhealthpk",
     "product": "bag-cutout.png", "product_pos": "top"}
  ]
`*word*` in a title is drawn in the accent colour; `\\n` breaks lines. Each card may override
"theme": {...}. Also used: "frame" (video inside a rounded border on the brand background).
"""
from __future__ import annotations

import html
import json
import math
import random

import shutil
from pathlib import Path

from common import die, need, run

HERE = Path(__file__).resolve().parent / "htmlcaps"
DEFAULT_THEME = {"bg1": "#1E8C3A", "bg2": "#0A3A17", "accent": "#F5C518", "ink": "#111111"}


def ease_out(x: float) -> float:
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def ease_back(x: float) -> float:
    x = min(max(x, 0.0), 1.0)
    c1 = 1.70158
    return 1 + (c1 + 1) * (x - 1) ** 3 + c1 * (x - 1) ** 2


def title_html(text: str) -> str:
    out = []
    for line in text.split("\n"):
        parts = []
        for w in line.split(" "):
            if len(w) > 2 and w.startswith("*") and w.endswith("*"):
                parts.append(f'<span class="a">{html.escape(w[1:-1])}</span>')
            else:
                parts.append(html.escape(w))
        out.append(" ".join(parts))
    return "<br>".join(out)


def card_frame(c: dict, t: float, dur: float, W: int, H: int, product: str | None, seed: int) -> str:
    th = {**DEFAULT_THEME, **c.get("_theme", {})}
    fade = min(1.0, t / 0.18, max(0.0, (dur - t) / 0.18))
    zoom = 1.04 - 0.04 * ease_out(t / 0.4)
    rnd = random.Random(seed)
    bokeh = []
    for _ in range(7):
        size = rnd.uniform(160, 460)
        x, y = rnd.uniform(-0.1, 0.9) * W, rnd.uniform(0.0, 1.0) * H
        bokeh.append(f'<div class="bokeh" style="width:{size:.0f}px;height:{size:.0f}px;left:{x:.0f}px;'
                     f'top:{y - t * 14:.0f}px;opacity:{rnd.uniform(.4, 1):.2f}"></div>')
    items, i = [], 0

    def anim(inner: str, cls: str = "") -> str:
        nonlocal i
        p = ease_out((t - 0.08 - 0.07 * i) / 0.35)
        i += 1
        return f'<div class="{cls}" style="opacity:{p:.3f};transform:translateY({(1 - p) * 40:.1f}px)">{inner}</div>'

    kind = c.get("type", "headline")
    if c.get("label"):
        items.append(anim(html.escape(c["label"]), "pill"))
    if kind in ("headline", "contact") and c.get("title"):
        items.append(anim(title_html(c["title"]), "title"))
    if c.get("sub"):
        items.append(anim(html.escape(c["sub"]), "sub"))
    if kind == "stats":
        for s in c.get("stats", []):
            items.append(anim(f'<div class="v">{html.escape(s["value"])}</div><div class="tag">{html.escape(s["tag"])}</div>', "stat"))
    if kind == "contact":
        rows = "".join(f'<div class="line">{html.escape(x)}</div>' for x in c.get("lines", []))
        phones = "<br>".join(html.escape(x) for x in c.get("phones", []))
        small = f'<div class="small">{html.escape(c["small"])}</div>' if c.get("small") else ""
        items.append(anim(f'{rows}{"<div class=phones>" + phones + "</div>" if phones else ""}{small}', "contact"))
    prod = ""
    if product:
        p = ease_back((t - 0.15) / 0.55)
        float_y = math.sin(t * 2.0) * 7 if t > 0.7 else 0
        size = float(c.get("product_size", 0.56))
        pos = c.get("product_pos", "bottom")
        place = {"bottom": "left:50%;bottom:8%;", "bottom-right": "left:auto;right:7%;bottom:9%;",
                 "top": "left:50%;top:10%;bottom:auto;", "center": "left:50%;top:50%;bottom:auto;"}[pos]
        tx = "translateX(-50%)" if "left:50%" in place else ""
        ty = " translateY(-50%)" if pos == "center" else ""
        scale = (0.55 + 0.45 * p) * (1 + 0.012 * t)
        prod = (f'<div class="product" style="{place}width:{size * 100:.1f}%;opacity:{min(1, p * 1.6):.3f};'
                f'transform:{tx}{ty} translateY({float_y:.1f}px) scale({scale:.4f})"><img src="file://{product}"></div>')
    top_off = c.get("stack_top")
    stack_style = f' style="top:{float(top_off) * 100:.1f}%"' if top_off is not None else ""
    align = " left" if c.get("align") == "left" else ""
    style = (f"--bg1:{th['bg1']};--bg2:{th['bg2']};--accent:{th['accent']};--ink:{th['ink']};"
             f"opacity:{fade:.3f};transform:scale({zoom:.4f})")
    return (f'<div class="card{align}" style="{style}">{"".join(bokeh)}'
            f'<div class="topline" style="width:{min(1, t / max(dur, .1)) * 100:.1f}%"></div>'
            f'<div class="stack"{stack_style}>{"".join(items)}</div>{prod}</div>')


def build(edit: dict, out_dir: Path, fps: int, total: float, fonts: list, resolve_src) -> Path:
    need("node")
    W, H = edit["output"]["width"], edit["output"]["height"]
    brand = {**DEFAULT_THEME, **(edit.get("brand") or {})}
    shutil.rmtree(out_dir, ignore_errors=True)
    out_dir.mkdir(parents=True)
    states, timeline, n = [], [], 0
    fdur = 1.0 / fps
    for ci, c in enumerate(sorted(edit.get("cards", []), key=lambda x: x["start"])):
        s0, s1 = float(c["start"]), min(float(c["end"]), total)
        if s1 - s0 < 0.3:
            die(f"card {ci + 1} is too short (min 0.3 s)")
        c = dict(c, _theme={**brand, **(c.get("theme") or {})})
        product = str(resolve_src(c["product"]).resolve()) if c.get("product") else None
        dur = s1 - s0
        k = 0
        while k * fdur < dur - 1e-6:
            t = k * fdur
            f = out_dir / f"k{n:05d}.png"
            n += 1
            states.append({"file": str(f), "html": card_frame(c, t, dur, W, H, product, ci)})
            timeline.append((s0 + t, min(s0 + t + fdur, s1), f))
            k += 1
    css = (HERE / "cards.css").read_text(encoding="utf-8")
    job = out_dir / "job.json"
    job.write_text(json.dumps({"width": W, "height": H, "css": css, "fonts": fonts, "states": states}), encoding="utf-8")
    run(["node", str(HERE / "render.js"), str(job)])
    from PIL import Image
    blank = out_dir / "blank.png"
    Image.new("RGBA", (W, H), (0, 0, 0, 0)).save(blank)
    entries, t = [], 0.0
    for a, b, f in timeline:
        if a > t + 1e-3:
            entries.append((blank, a - t))
        entries.append((f, b - max(a, t)))
        t = max(t, b)
    if t < total:
        entries.append((blank, total - t))
    lst = out_dir / "cards.ffconcat"
    body = ["ffconcat version 1.0"]
    for f, d in entries:
        body += [f"file '{Path(f).name}'", f"duration {d:.4f}"]
    body.append(f"file '{Path(entries[-1][0]).name}'")
    lst.write_text("\n".join(body) + "\n", encoding="utf-8")
    return lst


def frame_layers(edit: dict, work: Path) -> tuple[Path, Path, Path, tuple[int, int, int, int]]:
    """Background, rounded mask and border PNGs for the framed-footage look."""
    from PIL import Image, ImageDraw
    W, H = edit["output"]["width"], edit["output"]["height"]
    fr = edit["frame"]
    th = {**DEFAULT_THEME, **(edit.get("brand") or {})}
    m = int(W * float(fr.get("margin", 0.035)))
    top = int(H * float(fr.get("top", 0.03)))
    iw, ih = W - 2 * m, H - top - m
    rad = int(fr.get("radius", 44))
    bw = int(fr.get("border", 9))

    def rgb(h):
        h = h.lstrip("#")
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    c1, c2 = rgb(th["bg1"]), rgb(th["bg2"])
    bg = Image.new("RGB", (W, H))
    px = bg.load()
    for y in range(H):
        for x in range(0, W, 2):
            d = min(1.0, math.hypot((x - W / 2) / W, (y - H * .38) / H) * 1.6)
            col = tuple(int(c1[i] + (c2[i] - c1[i]) * d) for i in range(3))
            px[x, y] = col
            if x + 1 < W:
                px[x + 1, y] = col
    bgp, maskp, bordp = work / "frame_bg.png", work / "frame_mask.png", work / "frame_border.png"
    bg.save(bgp)
    ss = 3
    mk = Image.new("L", (iw * ss, ih * ss), 0)
    ImageDraw.Draw(mk).rounded_rectangle((0, 0, iw * ss - 1, ih * ss - 1), rad * ss, fill=255)
    mk.resize((iw, ih), Image.LANCZOS).save(maskp)
    bd = Image.new("RGBA", (W * ss, H * ss), (0, 0, 0, 0))
    ImageDraw.Draw(bd).rounded_rectangle((m * ss - bw * ss // 2, top * ss - bw * ss // 2, (m + iw) * ss + bw * ss // 2,
                                          (top + ih) * ss + bw * ss // 2), (rad + bw // 2) * ss,
                                         outline=rgb(fr.get("color", th["accent"])) + (255,), width=bw * ss)
    bd.resize((W, H), Image.LANCZOS).save(bordp)
    return bgp, maskp, bordp, (m, top, iw, ih)
