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
import re

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
    kind = c.get("type", "headline")
    if kind in ("section", "tag"):
        return swiss_frame(c, t, dur, W, H, th, fade)
    if kind == "panel":
        return panel_frame(c, t, dur, W, H, th, fade)
    if kind == "route":
        return route_frame(c, t, dur, W, H, th, fade)
    if kind == "trip":
        return trip_frame(c, t, dur, W, H, th, fade)
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
    if kind in ("headline", "contact", "map") and c.get("title"):
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
    mapsvg = map_svg(c, t, W, H, th) if kind == "map" else ""
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
    top_off = c.get("stack_top", c.get("_safe_top"))
    stack_style = f' style="top:{float(top_off) * 100:.1f}%"' if top_off is not None else ""
    align = " left" if c.get("align") == "left" else ""
    style = (f"--bg1:{th['bg1']};--bg2:{th['bg2']};--accent:{th['accent']};--ink:{th['ink']};"
             f"opacity:{fade:.3f};transform:scale({zoom:.4f})")
    return (f'<div class="card{align}" style="{style}">{"".join(bokeh)}'
            f'<div class="topline" style="width:{min(1, t / max(dur, .1)) * 100:.1f}%"></div>'
            f'{mapsvg}<div class="stack"{stack_style}>{"".join(items)}</div>{prod}</div>')


def panel_frame(c: dict, t: float, dur: float, W: int, H: int, th: dict, fade: float) -> str:
    """Explainer-UI panel (learned from an explainer reel): rounded dark (or light) card at the top with an
    optional 1..N step tracker, a small accent label, a pill, and text whose words light up over the
    card's duration; *word* = accent serif italic. "area": "top-half" fills the upper half (split screen)."""
    light = bool(c.get("light"))
    acc = th["accent"]
    steps = ""
    if c.get("steps"):
        n, cur = int(c["steps"]), int(c.get("step", 1))
        dots = []
        for i in range(1, n + 1):
            cls = "done" if i < cur else "cur" if i == cur else ""
            mark = "✓" if i < cur else str(i)
            dots.append(f'<span class="dot {cls}">{mark}</span>')
        steps = f'<div class="steps">{"".join(dots)}</div>'
    label = f'<div class="plabel">{html.escape(c["label"])}</div>' if c.get("label") else ""
    pill = f'<div class="ppill">{html.escape(c["pill"])}</div>' if c.get("pill") else ""
    words = c.get("text", "").split()
    lit = int(len(words) * min(1, max(0, (t - 0.15) / max(0.3, float(c.get("read_time", dur * 0.7))))) + 0.999)
    out = []
    for i, w in enumerate(words):
        star = len(w) > 2 and w.startswith("*") and w.endswith("*")
        txt = html.escape(w[1:-1] if star else w)
        out.append(f'<span class="{"em " if star else ""}{"on" if i < lit else "off"}">{txt}</span>')
    pop = ease_out(t / 0.3)
    area = c.get("area", "card")
    style = (f"--accent:{acc};opacity:{fade:.3f};transform:translateY({(1 - pop) * -30:.1f}px)")
    top = c.get("stack_top", c.get("_safe_top", 0.13))
    return (f'<div class="panel {"light" if light else ""} {area}" style="{style};top:{float(top) * 100:.1f}%">'
            f'{steps}{label}{pill}<div class="ptext">{" ".join(out)}</div></div>')


def swiss_frame(c: dict, t: float, dur: float, W: int, H: int, th: dict, fade: float) -> str:
    """Swiss-editorial inserts. section: solid colour card ("part / 2", "Framing / and / composition");
    tag: a translucent rounded colour box over the video whose wide-tracked caps type in letter by letter."""
    if c.get("type") == "tag":
        txt = c.get("text", "")
        n = int(len(txt) * min(1, max(0, (t - 0.15) / float(c.get("type_time", 0.45)))))
        bw, bh = float(c.get("w", 0.44)), float(c.get("h", 0.075))
        x, y = float(c.get("x", 0.5)), float(c.get("y", 0.2))
        pop = ease_back(t / 0.3)
        col = c.get("color", th["accent"])
        return (f'<div class="tagbox" style="left:{(x - bw / 2) * 100:.2f}%;top:{(y - bh / 2) * 100:.2f}%;'
                f'width:{bw * 100:.2f}%;height:{bh * 100:.2f}%;--c:{col};opacity:{fade:.3f};'
                f'transform:scale({0.7 + 0.3 * pop:.4f})"><span>{html.escape(txt[:n])}</span>'
                f'<span class="ghost">{html.escape(txt[n:])}</span></div>')
    bg = c.get("bg", th["accent"])
    ink = c.get("ink", "#111" if c.get("light") else "#fff")
    p1 = ease_out((t - 0.05) / 0.35)
    kicker = f'<div class="kicker" style="opacity:{p1:.3f}">{html.escape(c.get("kicker", ""))}</div>' if c.get("kicker") else ""
    num = (f'<div class="num" style="transform:scale({0.6 + 0.4 * ease_back((t - .1) / .4):.4f})">{html.escape(str(c["number"]))}</div>'
           if c.get("number") is not None else "")
    lines = []
    for j, ln in enumerate(c.get("title", "").split("\n")):
        pj = ease_out((t - 0.2 - 0.08 * j) / 0.35)
        m = re.fullmatch(r"\*(.+)\*", ln.strip())
        inner = f'<span class="bar">{html.escape(m.group(1))}</span>' if m else html.escape(ln)
        lines.append(f'<div class="tl" style="opacity:{pj:.3f};transform:translateX({(1 - pj) * -40:.1f}px)">{inner}</div>')
    top = c.get("stack_top", max(0.3, c.get("_safe_top", 0)))
    return (f'<div class="card section" style="background:{bg};color:{ink};--hi:{c.get("bar", "#E10600")};opacity:{fade:.3f}">'
            f'<div class="sw" style="top:{float(top) * 100:.1f}%">{kicker}{num}{"".join(lines)}</div></div>')


CITIES = {  # lat, lon
    "Sialkot": (32.49, 74.53), "Lahore": (31.55, 74.34), "Karachi": (24.86, 67.01), "Islamabad": (33.68, 73.05),
    "Faisalabad": (31.42, 73.08), "Multan": (30.20, 71.47), "Peshawar": (34.01, 71.58), "Quetta": (30.18, 66.98),
    "Gujranwala": (32.16, 74.19), "Khanpur": (28.65, 70.66), "Rahim Yar Khan": (28.42, 70.30), "Hyderabad": (25.40, 68.37), "Rawalpindi": (33.60, 73.04), "Sahiwal": (30.66, 73.11),
}


def img_ok(emoji: str) -> bool:
    """Download the Noto emoji PNG for the vehicle if it is not in assets/emoji yet."""
    try:
        from badge import emoji_png
        emoji_png(emoji)
        return True
    except BaseException:  # badge.die() raises SystemExit
        return False


def trip_frame(c: dict, t: float, dur: float, W: int, H: int, th: dict, fade: float) -> str:
    """Tiny trip bar near the top: FROM ● - - - 🛺 - - - ● TO, the vehicle drives along the dashed line.
    Keys: from, to (labels), vehicle (emoji), x, y, w (0-1), rtl (true: drives right -> left, Urdu reading order),
    drive_time (s), color."""
    from common import REPO
    w = W * float(c.get("w", 0.62))
    h = H * float(c.get("h", 0.055))
    x0, y0 = W * float(c.get("x", 0.5)) - w / 2, H * float(c.get("y", 0.13)) - h / 2
    acc = c.get("color", "#FFC93C")
    p = ease_out((t - 0.2) / float(c.get("drive_time", 1.6)))
    rtl = c.get("rtl", True)
    pad = h * 0.9
    fs = h * 0.42
    l_lbl, r_lbl = (c.get("to", ""), c.get("from", "")) if c.get("rtl", True) else (c.get("from", ""), c.get("to", ""))
    fs = min(fs, (w * 0.58 - pad * 1.1 - h) / max(1, (len(l_lbl) + len(r_lbl)) * 0.7))   # long names: smaller text, line stays >= ~40%
    lw = lambda s: len(s) * fs * 0.7 + h * 0.5        # label width + gap, so long names never run over the line
    lx0, lx1 = pad * .55 + max(h * 1.6, lw(l_lbl)), w - pad * .55 - max(h * 1.6, lw(r_lbl))
    img_ok(c.get("vehicle", "🛺"))
    vx = (lx1 - (lx1 - lx0) * p) if rtl else (lx0 + (lx1 - lx0) * p)
    cps = "_".join(f"{ord(ch):x}" for ch in c.get("vehicle", "🛺") if ord(ch) != 0xFE0F)
    img = REPO / "assets" / "emoji" / f"{cps}.png"
    vs = h * 1.25
    bounce = abs(math.sin(t * 18)) * h * 0.05
    flip = "scaleX(-1)" if not rtl else "none"
    left_lbl, right_lbl = (c.get("to", ""), c.get("from", "")) if rtl else (c.get("from", ""), c.get("to", ""))
    done_l = (lx1 - vx) if rtl else (vx - lx0)
    return (f'<div style="position:absolute;left:{x0:.0f}px;top:{y0:.0f}px;width:{w:.0f}px;height:{h:.0f}px;opacity:{fade:.3f};'
            f'border-radius:{h / 2:.0f}px;background:rgba(10,10,10,.55);border:1.5px solid rgba(255,255,255,.35);'
            f'box-shadow:0 8px 24px rgba(0,0,0,.3);font-family:Inter Tight,sans-serif;font-weight:800;color:#fff;">'
            f'<div style="position:absolute;left:{pad * .55:.0f}px;top:0;height:100%;display:flex;align-items:center;font-size:{fs:.0f}px">{html.escape(left_lbl)}</div>'
            f'<div style="position:absolute;right:{pad * .55:.0f}px;top:0;height:100%;display:flex;align-items:center;font-size:{fs:.0f}px">{html.escape(right_lbl)}</div>'
            f'<div style="position:absolute;left:{lx0:.0f}px;width:{lx1 - lx0:.0f}px;top:{h / 2 - 2:.0f}px;height:0;border-top:4px dotted rgba(255,255,255,.5)"></div>'
            f'<div style="position:absolute;left:{min(vx, lx1) if rtl else lx0:.0f}px;width:{max(done_l, 0):.0f}px;top:{h / 2 - 2:.0f}px;height:4px;background:{acc};border-radius:2px"></div>'
            f'<div style="position:absolute;left:{lx0 - 7:.0f}px;top:{h / 2 - 7:.0f}px;width:14px;height:14px;border-radius:50%;background:{acc if rtl and p >= 1 else "#fff"}"></div>'
            f'<div style="position:absolute;left:{lx1 - 7:.0f}px;top:{h / 2 - 7:.0f}px;width:14px;height:14px;border-radius:50%;background:#fff"></div>'
            f'<img src="file://{img}" style="position:absolute;left:{vx - vs / 2:.0f}px;top:{h / 2 - vs * 0.72 - bounce:.0f}px;width:{vs:.0f}px;height:{vs:.0f}px;transform:{flip}"></div>')


def route_frame(c: dict, t: float, dur: float, W: int, H: int, th: dict, fade: float) -> str:
    """Live-tracking widget (delivery-app look): a floating frosted panel over the video with a small
    Pakistan map, a dashed route that draws from `from` to `to`, a truck emoji driving along it, pins
    and a header "<label> / FROM -> TO". The rest of the frame stays transparent (video visible)."""
    from common import REPO
    geo = json.loads((REPO / "assets/maps/PAK.geo.json").read_text())
    geom = geo["features"][0]["geometry"]
    rings = [geom["coordinates"][0]] if geom["type"] == "Polygon" else [p[0] for p in geom["coordinates"]]
    lons = [x for r in rings for x, _ in r]
    lats = [y for r in rings for _, y in r]
    x0, y0, bw, bh = float(c.get("x", 0.46)), float(c.get("y", 0.3)), float(c.get("w", 0.76)), float(c.get("h", 0.3))
    PW, PH = W * bw, H * bh
    head = PH * 0.24
    k = math.cos(math.radians(30))
    mb = (PW * 0.06, head, PW * 0.88, PH - head - PH * 0.05)
    sc = min(mb[2] / ((max(lons) - min(lons)) * k), mb[3] / (max(lats) - min(lats)))
    ox = mb[0] + (mb[2] - (max(lons) - min(lons)) * k * sc) / 2
    oy = mb[1] + (mb[3] - (max(lats) - min(lats)) * sc) / 2

    def P(lat, lon):
        return ox + (lon - min(lons)) * k * sc, oy + (max(lats) - lat) * sc
    path = " ".join("M" + " L".join(f"{P(y, x)[0]:.1f},{P(y, x)[1]:.1f}" for x, y in r) + "Z" for r in rings)
    src, dst = c.get("from", "Karachi"), c.get("to", "Lahore")
    fx, fy = P(*CITIES[src])
    tx, ty = P(*CITIES[dst])
    cx, cy = (fx + tx) / 2 + (ty - fy) * 0.18, (fy + ty) / 2 - (tx - fx) * 0.05
    rt = float(c.get("route_time", 1.0))
    p = ease_out((t - 0.3) / rt)
    bx = (1 - p) ** 2 * fx + 2 * (1 - p) * p * cx + p ** 2 * tx
    by = (1 - p) ** 2 * fy + 2 * (1 - p) * p * cy + p ** 2 * ty
    pin = ease_back((t - 0.3 - rt) / 0.35)
    acc = c.get("color", th["accent"])
    pop = ease_back(t / 0.35)
    blink = 0.35 + 0.65 * (0.5 + 0.5 * math.cos(t * 9))
    truck = ""
    if c.get("vehicle", "🚚"):
        cps = "_".join(f"{ord(ch):x}" for ch in c.get("vehicle", "🚚") if ord(ch) != 0xFE0F)
        img = REPO / "assets" / "emoji" / f"{cps}.png"
        if img.exists():
            ts = PW * 0.13
            flip = -1 if tx > fx else 1  # emoji truck faces left: mirror it when driving right
            bounce = math.sin(t * 22) * 2
            truck = (f'<g transform="translate({bx:.1f} {by - ts * 0.55 + bounce:.1f}) scale({flip} 1)" opacity="{1 if p < 1 else max(0, 1 - (t - 0.3 - rt) / 0.3):.2f}">'
                     f'<image href="file://{img}" x="{-ts / 2:.1f}" y="{-ts / 2:.1f}" width="{ts:.1f}" height="{ts:.1f}"/></g>')
    fs = PH * 0.075
    svg = (f'<svg width="{PW:.0f}" height="{PH:.0f}" viewBox="0 0 {PW:.0f} {PH:.0f}" style="position:absolute;inset:0">'
           f'<defs><filter id="rg"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
           f'<mask id="rm"><path d="M{fx:.1f},{fy:.1f} Q{cx:.1f},{cy:.1f} {tx:.1f},{ty:.1f}" fill="none" stroke="#fff" stroke-width="16" pathLength="1" stroke-dasharray="1" stroke-dashoffset="{1 - p:.4f}"/></mask></defs>'
           f'<path d="{path}" fill="rgba(255,255,255,.10)" stroke="rgba(255,255,255,.55)" stroke-width="2.5" stroke-linejoin="round"/>'
           f'<path d="M{fx:.1f},{fy:.1f} Q{cx:.1f},{cy:.1f} {tx:.1f},{ty:.1f}" fill="none" stroke="{acc}" stroke-width="7" stroke-linecap="round" '
           f'stroke-dasharray="2 16" mask="url(#rm)" filter="url(#rg)"/>'
           f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="11" fill="#fff"/><circle cx="{fx:.1f}" cy="{fy:.1f}" r="22" fill="none" stroke="#fff" stroke-opacity=".5" stroke-width="3"/>'
           f'<text x="{fx + 30:.1f}" y="{fy + 10:.1f}" font-family="Inter Tight" font-weight="800" font-size="{fs * 0.62:.0f}" fill="#fff">{html.escape(src.upper())}</text>'
           f'<g transform="translate({tx:.1f} {ty:.1f}) scale({max(pin, 0):.3f})"><circle r="30" fill="{acc}" opacity=".3"/>'
           f'<path d="M0,0 C-22,-26 -26,-50 0,-64 C26,-50 22,-26 0,0Z" fill="{acc}" stroke="#fff" stroke-width="3"/><circle cy="-43" r="9" fill="#fff"/></g>'
           f'<text x="{tx - 40:.1f}" y="{ty - 72:.1f}" text-anchor="end" font-family="Inter Tight" font-weight="900" font-size="{fs * 0.8:.0f}" fill="#fff" opacity="{min(1, max(pin, 0)):.2f}">{html.escape(dst.upper())}</text>'
           f'{truck}</svg>')
    header = (f'<div class="rt-head" style="height:{head:.0f}px;padding:0 {PW * 0.06:.0f}px">'
              f'<div class="rt-label" style="font-size:{fs * 0.62:.0f}px"><span class="rt-dot" style="background:{acc};opacity:{blink:.2f}"></span>{html.escape(c.get("label", "On the way"))}</div>'
              f'<div class="rt-title" style="font-size:{fs * 1.15:.0f}px">{html.escape(c.get("title", src + " → " + dst))}</div></div>')
    return (f'<div class="routebox" style="left:{(x0 - bw / 2) * 100:.2f}%;top:{(y0 - bh / 2) * 100:.2f}%;width:{PW:.0f}px;height:{PH:.0f}px;'
            f'opacity:{fade:.3f};transform:scale({0.8 + 0.2 * pop:.4f})">{header}{svg}</div>')


def map_svg(c: dict, t: float, W: int, H: int, th: dict) -> str:
    """Pakistan map with a route drawing to the destination, pin drop and a slow camera push."""
    from common import REPO
    geo = json.loads((REPO / c.get("geo", "assets/maps/PAK.geo.json")).read_text())
    geom = geo["features"][0]["geometry"]
    rings = [geom["coordinates"][0]] if geom["type"] == "Polygon" else [p[0] for p in geom["coordinates"]]
    lons = [x for r in rings for x, _ in r]
    lats = [y for r in rings for _, y in r]
    mt = float(c.get("map_top", 0.36 if c.get("title") else 0.27))
    box = (W * 0.08, H * mt, W * 0.8, H * (0.86 - mt))  # x, y, w, h (below the title)
    k = math.cos(math.radians(30))
    sx = box[2] / ((max(lons) - min(lons)) * k)
    sy = box[3] / (max(lats) - min(lats))
    sc = min(sx, sy)
    ox = box[0] + (box[2] - (max(lons) - min(lons)) * k * sc) / 2
    oy = box[1] + (box[3] - (max(lats) - min(lats)) * sc) / 2

    def P(lat, lon):
        return ox + (lon - min(lons)) * k * sc, oy + (max(lats) - lat) * sc
    path = " ".join("M" + " L".join(f"{P(y, x)[0]:.1f},{P(y, x)[1]:.1f}" for x, y in r) + "Z" for r in rings)
    dest = c.get("to", "Sialkot")
    tx, ty = P(*CITIES[dest]) if isinstance(dest, str) else P(*dest)
    src = c.get("from")
    if src:
        fx, fy = P(*CITIES[src]) if isinstance(src, str) else P(*src)
    else:  # unlabeled start in the south-west of the map
        fx, fy = P(28.0, 68.8)
    cx, cy = (fx + tx) / 2 - (ty - fy) * 0.25, (fy + ty) / 2 + (tx - fx) * 0.12
    p = ease_out((t - 0.25) / float(c.get("route_time", 1.1)))
    bx = (1 - p) ** 2 * fx + 2 * (1 - p) * p * cx + p ** 2 * tx
    by = (1 - p) ** 2 * fy + 2 * (1 - p) * p * cy + p ** 2 * ty
    pin = ease_back((t - 0.25 - float(c.get("route_time", 1.1))) / 0.35)
    zoom = 1 + 0.12 * ease_out((t - 0.3) / 2.2)
    acc = th["accent"]
    others = "".join(
        f'<circle cx="{P(*ll)[0]:.1f}" cy="{P(*ll)[1]:.1f}" r="5" fill="rgba(255,255,255,.35)"/>'
        for name, ll in CITIES.items() if name != dest and name in ("Lahore", "Karachi", "Islamabad", "Faisalabad", "Multan"))
    label = c.get("pin_label", dest if isinstance(dest, str) else "")
    src_label = (f'<text x="{fx:.1f}" y="{fy + 46:.1f}" text-anchor="middle" font-family="Poppins SemiBold" font-size="26" '
                 f'fill="rgba(255,255,255,.75)">{html.escape(c.get("from_label", src or ""))}</text>') if (src or c.get("from_label")) else ""
    return (f'<svg width="{W}" height="{H}" style="position:absolute;inset:0" viewBox="0 0 {W} {H}">'
            f'<defs><filter id="gl"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/>'
            f'<feMergeNode in="SourceGraphic"/></feMerge></filter></defs>'
            f'<g transform="translate({tx:.1f} {ty:.1f}) scale({zoom:.4f}) translate({-tx:.1f} {-ty:.1f})">'
            f'<path d="{path}" fill="rgba(255,255,255,.07)" stroke="{acc}" stroke-width="3" stroke-linejoin="round" filter="url(#gl)" opacity=".9"/>'
            f'{others}'
            f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="9" fill="#fff"/>{src_label}'
            f'<path d="M{fx:.1f},{fy:.1f} Q{cx:.1f},{cy:.1f} {tx:.1f},{ty:.1f}" fill="none" stroke="#fff" stroke-width="6" '
            f'stroke-linecap="round" stroke-dasharray="14 12" pathLength="1000" opacity=".9" '
            f'style="stroke-dashoffset:0;clip-path:none" mask="url(#rv)"/>'
            f'<mask id="rv"><path d="M{fx:.1f},{fy:.1f} Q{cx:.1f},{cy:.1f} {tx:.1f},{ty:.1f}" fill="none" stroke="#fff" stroke-width="14" '
            f'pathLength="1" stroke-dasharray="1" stroke-dashoffset="{1 - p:.4f}"/></mask>'
            f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="13" fill="{acc}" filter="url(#gl)" opacity="{1 if 0 < p < 1 else 0}"/>'
            f'<g transform="translate({tx:.1f} {ty:.1f}) scale({max(pin, 0):.3f})">'
            f'<circle r="34" fill="{acc}" opacity=".25"/>'
            f'<path d="M0,0 C-26,-30 -30,-58 0,-74 C30,-58 26,-30 0,0Z" fill="{acc}" stroke="#111" stroke-width="3"/>'
            f'<circle cy="-50" r="10" fill="#111"/></g>'
            f'<text x="{tx + (46 if tx < W * 0.6 else -46):.1f}" y="{ty - 30:.1f}" text-anchor="{"start" if tx < W * 0.6 else "end"}" font-family="Oswald" font-weight="700" font-size="64" fill="#fff" '
            f'opacity="{min(1, max(pin, 0)):.2f}" style="text-transform:uppercase">{html.escape(label.upper())}</text>'
            f'</g></svg>')


def build(edit: dict, out_dir: Path, fps: int, total: float, fonts: list, resolve_src) -> Path:
    need("node")
    OW, OH = edit["output"]["width"], edit["output"]["height"]
    sc = OW / 1080 if OW > 1080 else 1  # 4K: lay out at 1080 wide, rasterise at device scale (sharp, same design)
    W, H = round(OW / sc), round(OH / sc)
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
        if edit.get("safe"):
            c["_safe_top"] = max(0.09, float(edit["safe"].get("top", 0)) + 0.02)
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
    job.write_text(json.dumps({"width": W, "height": H, "scale": sc, "css": css, "fonts": fonts, "states": states}), encoding="utf-8")
    run(["node", str(HERE / "render.js"), str(job)])
    from PIL import Image
    blank = out_dir / "blank.png"
    Image.new("RGBA", (OW, OH), (0, 0, 0, 0)).save(blank)
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
    if fr.get("layout") == "split":  # explainer split screen: speaker card in the lower half
        top = int(H * float(fr.get("split", 0.5)))
        m = int(W * float(fr.get("margin", 0.08)))
        iw, ih = W - 2 * m, H - top - int(H * 0.06)
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
