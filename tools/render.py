#!/usr/bin/env python3
"""Render the final video from an approved edit.json.

    python tools/render.py "Video Edits/Export/my-reel/edit.json" --preview   # fast, small check
    python tools/render.py "Video Edits/Export/my-reel/edit.json"             # full quality

Output: Export/<project>/<project>.mp4 (or <project>_preview.mp4).
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import time
from pathlib import Path

import edl
from common import REPO, die, encode_layer, font_files, fmt_time, load_json, need, resolve, run

AUDIO_FMT = "aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo"


# ---------------------------------------------------------------- text overlay (ASS)

def ass_color(c: str, alpha: int = 0) -> str:
    named = {"white": "#FFFFFF", "black": "#000000", "yellow": "#FFE600", "red": "#FF2D2D",
             "green": "#2DFF6A", "blue": "#2D8CFF", "orange": "#FF8A00", "pink": "#FF4FD8"}
    c = named.get(str(c).lower(), c).lstrip("#")
    if len(c) != 6:
        die(f"bad colour '{c}' (use #RRGGBB or a name like white/yellow)")
    return f"&H{alpha:02X}{c[4:6]}{c[2:4]}{c[0:2]}".upper()


def ass_time(t: float) -> str:
    cs = int(round(max(t, 0) * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def ass_text(s: str) -> str:
    return s.replace("\\", "\\\\").replace("{", "(").replace("}", ")").replace("\n", "\\N")


def style_line(name: str, st: dict, H: int, default_size: float, align: int) -> str:
    size = int(H * float(st.get("size", default_size)) / 100)
    outline = st.get("outline", 0.35)
    box = st.get("box", False)
    return ("Style: {n},{font},{size},{pc},{sc},{oc},{bc},{bold},{it},0,0,100,100,0,0,{bs},{ol},{sh},{al},60,60,{mv},1"
            .format(n=name, font=st.get("font", "DejaVu Sans"), size=size,
                    pc=ass_color(st.get("color", "white")), sc=ass_color(st.get("color", "white")),
                    oc=ass_color(st.get("box_color", "black"), 0x40) if box else ass_color(st.get("outline_color", "black"), int(st.get("outline_alpha", 0))),
                    bc=ass_color(st.get("shadow_color", "#000000"), int(st.get("shadow_alpha", 0x80))),
                    bold=-1 if st.get("bold", True) else 0, it=-1 if st.get("italic") else 0,
                    bs=3 if box else 1, ol=round(size * outline / 10, 1) if not box else round(size * 0.25),
                    sh=st.get("shadow", 0), al=align, mv=int(H * float(st.get("margin", 12)) / 100)))


def anchor(x: dict, W: int, H: int, mv: int) -> tuple[int, int]:
    if "x" in x or "y" in x:
        return int(W * float(x.get("x", 0.5))), int(H * float(x.get("y", 0.5)))
    return {"top": (W // 2, mv), "center": (W // 2, H // 2), "bottom": (W // 2, H - mv)}[x["position"]]


def text_fx(anim: str, x0: int, y0: int, W: int, H: int, has_pos: bool) -> str:
    pos = f"\\pos({x0},{y0})" if has_pos else ""
    return {
        "none": pos,
        "fade": pos + "\\fad(200,200)",
        "pop": pos + "\\fad(80,150)\\fscx40\\fscy40\\t(0,160,\\fscx115\\fscy115)\\t(160,280,\\fscx100\\fscy100)",
        "slide_up": f"\\move({x0},{y0 + int(H * 0.06)},{x0},{y0},0,300)\\fad(200,150)",
        "slide_left": f"\\move({x0 + W // 2},{y0},{x0},{y0},0,320)\\fad(100,150)",
        "typewriter": pos + "\\fad(0,150)",
    }[anim]


def typewriter(text: str, step_ms: int = 110) -> str:
    out, j = [], 0
    for line in text.split("\n"):
        words = []
        for w in line.split(" "):
            t0 = j * step_ms
            words.append("{\\alpha&HFF&\\t(%d,%d,\\alpha&H00&)}%s" % (t0, t0 + 60, ass_text(w)))
            j += 1
        out.append(" ".join(words))
    return "\\N".join(out)


def segments_text(segs: list, presets: dict, H: int) -> str:
    """Mixed typography in one block: each segment has its own font/size/colour.
    {"text": "8cr+", "preset": "serif"} or explicit font/size/italic/bold/color; "newline": true starts a new line."""
    out = []
    for i, sg in enumerate(segs):
        sg = {**presets.get(sg.get("preset", ""), {}), **sg}
        tags = ""
        if sg.get("font"):
            tags += "\\fn" + sg["font"]
        if sg.get("size"):
            tags += f"\\fs{int(H * float(sg['size']) / 100)}"
        if "italic" in sg:
            tags += f"\\i{1 if sg['italic'] else 0}"
        if "bold" in sg:
            tags += f"\\b{1 if sg['bold'] else 0}"
        if sg.get("color"):
            tags += "\\c" + ass_color(sg["color"])
        if sg.get("hollow"):  # outline-only letters (stroke in `color`, transparent fill)
            tags += f"\\1a&HFF&\\3c{ass_color(sg.get('color', '#FFFFFF'))}\\bord{float(sg.get('stroke', 2.2)) * H / 1920:.1f}\\shad0"
        else:  # reset after a hollow segment
            tags += f"\\1a&H00&\\bord{float(sg.get('stroke', 0)) * H / 1920:.1f}" if any(x.get("hollow") for x in segs) else (
                f"\\bord{float(sg['stroke']) * H / 1920:.1f}" if "stroke" in sg else "")
        if sg.get("spacing") is not None:  # letter spacing in px at 1080 wide
            tags += f"\\fsp{float(sg['spacing']) * H / 1920:.1f}"
        text = sg["text"].upper() if sg.get("uppercase") else sg["text"].lower() if sg.get("lowercase") else sg["text"]
        sep = "" if i == 0 else ("\\N" if sg.get("newline") else "" if sg.get("attach") else " ")
        out.append(f"{sep}{{{tags}}}{ass_text(text)}")
    return "".join(out)


STOPWORDS = set("""hai hain ka ki ke ko se mein main aur to yeh ye woh wo bhai ne bhi hon ho kar ja
chahe hoti hota parti padti kyunke kyun liye sab diya dala lekar wahi bas abhi
raha rahe rahi wala wali wale is us in un ek koi kya na nahi tha thi the hi par pe aap hum
the a an the of to in on and or is are was it for with at by this that you your""".split())


def plan_kinetic(lines: list, cap: dict) -> list:
    """For each caption line, pick the word to show big (index or None)."""
    kc = cap.get("style", {}).get("kinetic", {})
    kw = {k.lower() for k in (cap.get("keywords") or {})}
    min_len = int(kc.get("min_len", 4))
    stop = STOPWORDS | {w.lower() for w in kc.get("stopwords", [])}
    plan = []
    manual = any(w.get("big") for ln in lines for w in (ln.get("words") or []))
    for ln in lines:
        wl = ln.get("words") or []
        if manual:  # words marked *like this* in captions.txt decide; unmarked lines have no big word
            plan.append(next((i for i, w in enumerate(wl) if w.get("big")), None))
            continue
        words = [re.sub(r"[^\w]", "", w["text"].lower()) for w in wl]
        pick = next((i for i, w in enumerate(words) if w in kw), None)
        if pick is None:
            cands = [(len(w), -i, i) for i, w in enumerate(words) if w not in stop and len(w) >= min_len]
            pick = max(cands)[2] if cands else None
        plan.append(pick)
    return plan


def kinetic_events(lines: list, cap: dict, W: int, H: int, glow: str, pos: str) -> list:
    """Kinetic captions: small words + one big word per line in alternating display fonts,
    stacked (before / BIG / after); words appear one by one as they are spoken and pop in."""
    st = cap.get("style", {})
    kc = st.get("kinetic", {})
    small = {"font": "Poppins SemiBold", "size": 4.0, "color": "white", **kc.get("small", {})}
    bigs = kc.get("big") or [{"font": "Instrument Serif", "italic": True, "size": 11, "color": "white"},
                             {"font": "Anton", "size": 8.5, "color": "#FFD400", "uppercase": True}]
    kw = {k.lower(): v for k, v in (cap.get("keywords") or {}).items()}
    plain = {**small, "size": float(small["size"]) * float(kc.get("no_big_scale", 1.3))}
    lower = st.get("lowercase", True)

    def tags(v: dict, hidden: bool, popin: bool) -> str:
        t = "\\r" + glow
        t += "\\fn" + v["font"] + f"\\fs{int(H * float(v['size']) / 100)}" + "\\c" + ass_color(v.get("color", "white"))
        t += f"\\i{1 if v.get('italic') else 0}\\b0"
        if hidden:
            t += "\\alpha&HFF&"
        elif popin:
            t += "\\fscx45\\fscy45\\t(0,110,\\fscx108\\fscy108)\\t(110,190,\\fscx100\\fscy100)"
        return "{" + t + "}"

    events, plan, bi = [], plan_kinetic(lines, cap), 0
    for ln, pick in zip(lines, plan):
        words = ln.get("words") or []
        if not words:
            continue
        looks = []
        for i, w in enumerate(words):
            key = re.sub(r"[^\w]", "", w["text"].lower())
            if key in kw:
                looks.append({**bigs[-1], **kw[key]})
            elif i == pick:
                looks.append(bigs[bi % len(bigs)])
            else:
                looks.append(small if pick is not None else plain)
        if pick is not None:
            bi += 1
        texts = []
        for w, v in zip(words, looks):
            t = w["text"]
            texts.append(t.upper() if v.get("uppercase") else t.lower() if lower and v is not bigs[0] else t)
        # stacked layout: words before the big word / big word / words after
        groups = [[i for i in range(len(words)) if pick is None or i < pick], [pick] if pick is not None else [],
                  [i for i in range(len(words)) if pick is not None and i > pick]]
        groups = [gq for gq in groups if gq]
        for k in range(len(words)):
            a = words[k]["start"] if k else ln["start"]
            b = words[k + 1]["start"] if k + 1 < len(words) else ln["end"]
            if b <= a:
                continue
            rows = []
            for gq in groups:
                row = " ".join(tags(looks[i], i > k, i == k) + ass_text(texts[i]) for i in gq if texts[i] != "_")
                if row:
                    rows.append(row)
            events.append(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},Cap,,0,0,0,,{{{pos}}}" + "\\N".join(rows))
    return events


def lower_third(i: int, x: dict, W: int, H: int, styles: list, events: list) -> None:
    size = H * float(x.get("size", 3.4)) / 100
    sub = x.get("subtext", "")
    ssize = H * float(x.get("subsize", 2.3)) / 100
    styles.append(style_line(f"LT{i}", {**x, "outline": 0, "size": x.get("size", 3.4), "color": x.get("text_color", "white")}, H, 3.4, 7))
    styles.append(style_line(f"LS{i}", {**x, "outline": 0, "bold": False, "size": x.get("subsize", 2.3),
                                        "color": x.get("subtext_color", x.get("text_color", "white"))}, H, 2.3, 7))
    pad = int(size * 0.35)
    bw = int(max(len(x["text"]) * size * 0.58, len(sub) * ssize * 0.55) + 2 * pad)
    bh = int(size * 1.25 + (ssize * 1.35 if sub else 0) + pad)
    x0, y0 = int(W * float(x.get("x", 0.06))), int(H * float(x.get("y", 0.64)))
    a, b = ass_time(x.get("start", 0)), ass_time(x["end"])
    col = ass_color(x.get("color", "#E91E63"))
    events.append(f"Dialogue: 2,{a},{b},LT{i},,0,0,0,,{{\\an7\\move({x0 - bw - 40},{y0},{x0},{y0},0,350)\\p1\\bord0\\shad0"
                  f"\\1c{col}\\fad(0,250)}}m 0 0 l {bw} 0 {bw} {bh} 0 {bh}{{\\p0}}")
    events.append(f"Dialogue: 3,{a},{b},LT{i},,0,0,0,,{{\\an7\\move({x0 - bw},{y0 + pad // 2},{x0 + pad},{y0 + pad // 2},120,450)"
                  f"\\fad(150,250)}}{ass_text(x['text'])}")
    if sub:
        ys = y0 + pad // 2 + int(size * 1.2)
        events.append(f"Dialogue: 3,{a},{b},LS{i},,0,0,0,,{{\\an7\\move({x0 - bw},{ys},{x0 + pad},{ys},200,520)"
                      f"\\fad(200,250)}}{ass_text(sub)}")


def build_ass(edit: dict, path: Path) -> bool:
    W, H = edit["output"]["width"], edit["output"]["height"]
    styles, events = [], []
    for i, x in enumerate(edit["texts"]):
        if x.get("type") == "lower_third":
            lower_third(i, x, W, H, styles, events)
            continue
        name = f"T{i}"
        al = {"left": 7, "right": 9}.get(x.get("align"), edl.POSITIONS[x.get("position", "top")])
        styles.append(style_line(name, x, H, 5.0, al))
        anim = x.get("animation", "fade")
        mv = int(H * float(x.get("margin", 12)) / 100)
        x0, y0 = anchor(x, W, H, mv)
        has_pos = "x" in x or "y" in x
        fx = text_fx(anim, x0, y0, W, H, has_pos)
        if x.get("segments"):
            body = segments_text(x["segments"], edit.get("type_presets", {}), H)
        else:
            body = typewriter(x["text"]) if anim == "typewriter" else ass_text(x["text"])
        events.append(f"Dialogue: 1,{ass_time(x.get('start', 0))},{ass_time(x['end'])},{name},,0,0,0,,{{{fx}}}{body}")

    for k, gl in enumerate(edit.get("glass", [])):
        if gl.get("value"):  # iOS-style liquid-glass widget: dot + label, big value, small line (left aligned)
            x0, y0, bw, bh = glass_box(gl, W, H)
            pad = min(int(min(bw, bh) * float(gl.get("pad", 0.16))), int(W * 0.06))
            vs = int(bh * float(gl.get("value_size", 0.34)))
            ls = int(bh * 0.13)
            dot = gl.get("dot", "#E8553B")
            styles.append(style_line(f"GW{k}", {"font": "Inter Tight", "bold": False, "size": 100 * ls / H,
                                                "color": gl.get("text_color", "#FFFFFF"), "outline": 0, "shadow": 0}, H, 2, 7))
            s0, s1 = float(gl.get("start", 0)), float(gl.get("end", edit["_total"]))
            fd = "\\fad(250,250)"
            ev = []
            if gl.get("label"):
                ev.append((y0 + pad, "{\\c" + ass_color(dot) + "}●{\\c" + ass_color(gl.get("text_color", "#FFFFFF")) + "} " + ass_text(gl["label"]), ls, gl.get("label_font", "Inter Tight"), 0))
            ev.append((y0 + pad + int(ls * 1.5), ass_text(gl["value"]), vs, gl.get("value_font", "Inter Tight"), 1))
            if gl.get("sub"):  # anchored to the box bottom so it never spills out
                # stylish sub line: own font / size / colour / italic (style glass.widget sub_*)
                sub_tags = ""
                if gl.get("sub_color"):
                    sub_tags += "\\c" + ass_color(gl["sub_color"])
                if gl.get("sub_italic"):
                    sub_tags += "\\i1"
                if gl.get("sub_spacing"):
                    sub_tags += f"\\fsp{gl['sub_spacing']}"
                sub_txt = ("{" + sub_tags + "}" if sub_tags else "") + ass_text(gl["sub"])
                ev.append((y0 + bh - int(pad * 0.8), sub_txt, int(ls * float(gl.get("sub_size", 1))),
                           gl.get("sub_font", "Inter Tight"), 0))
            # shrink the value if label + value lines + sub would not fit inside the box
            nl = str(gl["value"]).count("\n") + 1
            room = bh - 2 * pad - (int(ls * 1.5) if gl.get("label") else 0) - (int(ls * 1.3) if gl.get("sub") else 0)
            if vs * (nl - 0.1) > room:
                vs = max(int(room / (nl - 0.1)), ls)
                ev = [(y, t, vs if b else s, f, b) for y, t, s, f, b in ev]
            for i, (yy, txt, size, fn, bold) in enumerate(ev):
                an = 1 if (gl.get("sub") and i == len(ev) - 1) else 7
                events.append(f"Dialogue: 4,{ass_time(s0)},{ass_time(s1)},GW{k},,0,0,0,,"
                              f"{{\\an{an}\\pos({x0 + pad},{yy})\\fn{fn}\\fs{size}\\b{bold}{fd}}}{txt}")
            continue
        if not gl.get("text"):
            continue
        x0, y0, bw, bh = glass_box(gl, W, H)
        st = {"font": gl.get("font", "Poppins SemiBold"), "bold": False, "size": gl.get("size", 3.6),
              "color": gl.get("color", "white"), "outline": 0, "shadow": 2, "shadow_alpha": 140}
        styles.append(style_line(f"G{k}", st, H, 3.2, 5))
        body = ass_text(gl["text"])
        if gl.get("subtext"):
            body += "\\N{\\fs" + str(int(H * float(gl.get("size", 3.2)) * 0.55 / 100)) + "\\alpha&H40&}" + ass_text(gl["subtext"])
        s0, s1 = float(gl.get("start", 0)), float(gl.get("end", edit["_total"]))
        events.append(f"Dialogue: 4,{ass_time(s0)},{ass_time(s1)},G{k},,0,0,0,,{{\\an5\\pos({x0 + bw // 2},{y0 + bh // 2})\\fad(250,250)}}{body}")

    cap = edit.get("captions")
    if cap:
        cfile = edit["_dir"] / cap.get("file", "captions.json")
        if not cfile.exists():
            die(f"{cfile.relative_to(REPO)} not found. Run: python tools/captions.py \"{edit['_path'].relative_to(REPO).as_posix()}\"")
        st = cap.get("style", {})
        styles.append(style_line("Cap", st, H, 4.2, edl.POSITIONS[st.get("position", "bottom")]))
        hi = st.get("highlight_color")
        hscale = int(float(st.get("highlight_scale", 1.0)) * 100)
        upper = st.get("uppercase", False)
        lower = st.get("lowercase", False)
        case = (lambda v: v.upper()) if upper else (lambda v: v.lower()) if lower else (lambda v: v)
        pos = f"\\an5\\pos({W // 2},{int(H * float(st['y']))})" if "y" in st else ""
        anim = {"pop": "\\fscx70\\fscy70\\t(0,120,\\fscx100\\fscy100)", "fade": "\\fad(120,80)"}.get(st.get("animation"), "")
        glow = f"\\blur{float(st['glow'])}" if st.get("glow") else ""
        pop = "{" + pos + glow + anim + "}" if pos or anim or glow else ""
        keep = "{" + pos + glow + "}" if pos or glow else ""
        kw = {k.lower(): v for k, v in (cap.get("keywords") or {}).items()}

        def styled(word: str) -> str:
            k = re.sub(r"[^\w]", "", word.lower())
            if k not in kw:
                return ass_text(case(word))
            v = kw[k]
            tags = ""
            if v.get("font"):
                tags += "\\fn" + v["font"]
            if v.get("size"):
                tags += f"\\fs{int(H * float(v['size']) / 100)}"
            if v.get("color"):
                tags += "\\c" + ass_color(v["color"])
            if "italic" in v:
                tags += f"\\i{1 if v['italic'] else 0}"
            text = word.upper() if v.get("uppercase") else case(word)
            return "{" + tags + "}" + ass_text(text) + "{\\r" + glow + "}"
        all_lines = load_json(cfile)["lines"]
        spans = [(float(c["start"]), float(c["end"])) for c in edit.get("cards", [])]
        all_lines = [ln for ln in all_lines if not any(a - 0.05 <= ln["start"] < b for a, b in spans)]
        if st.get("mode") == "html":
            all_lines = []
        elif st.get("mode") == "kinetic":
            events += kinetic_events(all_lines, cap, W, H, glow, pos or f"\\an5\\pos({W // 2},{int(H * 0.68)})")
            all_lines = []
        for ln in all_lines:
            text = case(ln["text"])
            words = ln.get("words") or []
            if hi and words and " ".join(w["text"] for w in words) == ln["text"]:
                # one event per spoken word, with that word highlighted
                parts = [styled(w["text"]) for w in words]
                for k, w in enumerate(words):
                    a = w["start"] if k else ln["start"]
                    b = words[k + 1]["start"] if k + 1 < len(words) else ln["end"]
                    big = f"\\fscx{hscale}\\fscy{hscale}" if hscale != 100 else ""
                    shown = list(parts)
                    shown[k] = "{\\c" + ass_color(hi) + big + "}" + parts[k] + "{\\r" + glow + "}"
                    events.append(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},Cap,,0,0,0,,{pop if k == 0 else keep}{' '.join(shown)}")
            else:
                events.append(f"Dialogue: 0,{ass_time(ln['start'])},{ass_time(ln['end'])},Cap,,0,0,0,,{pop}{' '.join(styled(w) for w in text.split(' '))}")
    if not events:
        return False
    head = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 0",
            "ScaledBorderAndShadow: yes", "", "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
            "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding"]
    body = ["", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    path.write_text("\n".join(head + styles + body + events) + "\n", encoding="utf-8")
    return True


# ---------------------------------------------------------------- filter graph

def atempo(speed: float) -> str:
    parts = []
    while speed > 2.0:
        parts.append("atempo=2.0")
        speed /= 2.0
    while speed < 0.5:
        parts.append("atempo=0.5")
        speed /= 0.5
    parts.append(f"atempo={speed:.4f}")
    return ",".join(parts)


def esc(p: str) -> str:
    return p.replace("\\", "/").replace(":", "\\:").replace("'", "\\'")


def build_graph(edit: dict, work: Path, preview: bool) -> tuple[list[str], str, str, str]:
    o = edit["output"]
    fps = o["fps"]
    inputs, g = [], []
    for s in edit["shots"]:
        n = s["_n"]
        idx = inputs.count("-i")
        inputs += ["-ss", f"{s['in']:.3f}", "-t", f"{s['out'] - s['in']:.3f}", "-i", str(s["_src"])]
        L = s["_len"]
        sp = f",setpts=PTS/{s['speed']}" if s["speed"] != 1 else ""
        g.append(f"[{idx}:v]setpts=PTS-STARTPTS{sp}[r{n}]")
        g.append(edl.fit_filter(edit, s, f"[r{n}]", f"[f{n}]"))
        g.append(f"[f{n}]fps={fps}{edl.motion_filter(edit, s)},format=yuv420p,trim=duration={L:.3f},setpts=PTS-STARTPTS,settb=AVTB[v{n}]")
        vol = float(s.get("volume", 1.0))
        if s["_info"]["has_audio"] and not s.get("mute"):
            g.append(f"[{idx}:a]asetpts=PTS-STARTPTS,{atempo(s['speed'])},{AUDIO_FMT},volume={vol},"
                     f"apad,atrim=duration={L:.3f},asetpts=PTS-STARTPTS[a{n}]")
        else:
            g.append(f"anullsrc=r=48000:cl=stereo,atrim=duration={L:.3f},{AUDIO_FMT}[a{n}]")

    # join shots: hard cuts with concat, transitions with xfade/acrossfade
    shots = edit["shots"]
    cv, ca, length = "[v1]", "[a1]", shots[0]["_len"]
    for prev, s in zip(shots, shots[1:]):
        n, tr = s["_n"], prev["transition"]
        if tr["duration"] > 0:
            d = tr["duration"]
            g.append(f"{cv}[v{n}]xfade=transition={tr['type']}:duration={d}:offset={length - d:.3f}[jv{n}]")
            g.append(f"{ca}[a{n}]acrossfade=d={d}[ja{n}]")
            length += s["_len"] - d
        else:
            g.append(f"{cv}{ca}[v{n}][a{n}]concat=n=2:v=1:a=1[jv{n}][ja{n}]")
            length += s["_len"]
        cv, ca = f"[jv{n}]", f"[ja{n}]"
    total = edit["_total"]

    # picture: look, stickers/images, progress bar, text, fades, preview scale
    W, H = o["width"], o["height"]
    vf = []
    look = edit.get("look") or {}
    if any(k in look for k in ("brightness", "contrast", "saturation", "gamma")):
        vf.append("eq=" + ":".join(f"{k}={look[k]}" for k in ("brightness", "contrast", "saturation", "gamma") if k in look))
    if look.get("cinematic"):  # light film look that keeps the picture crisp: S-curve, teal shadows / warm highlights
        c = float(look["cinematic"])
        vf.append(f"curves=master='0/0 0.22/{0.22 - 0.04 * c:.3f} 0.5/0.5 0.78/{0.78 + 0.04 * c:.3f} 1/1'")
        vf.append(f"colorbalance=rs={-0.04 * c:.3f}:bs={0.05 * c:.3f}:rh={0.045 * c:.3f}:bh={-0.04 * c:.3f}")
    if look.get("warmth"):  # + warmer, - cooler
        wv = float(look["warmth"])
        vf.append(f"colorbalance=rm={wv:.3f}:bm={-wv:.3f}:rh={wv / 2:.3f}:bh={-wv / 2:.3f}")
    if look.get("denoise"):  # clean phone-video noise / compression blocks before sharpening (keeps edges)
        dn = float(look["denoise"])
        vf.append(f"hqdn3d={1.2 * dn:.2f}:{1.0 * dn:.2f}:{3 * dn:.2f}:{2.5 * dn:.2f}")
    if look.get("sharpen"):
        vf.append(f"unsharp=5:5:{float(look['sharpen'])}:5:5:0")
    if look.get("grain"):  # light film grain for a cinematic touch (applied under text and stickers)
        vf.append(f"noise=alls={int(look['grain'])}:allf=t")
    if look.get("vignette"):
        vf.append(f"vignette=angle={float(look['vignette']):.3f}")
    if look.get("lut"):
        lut = resolve(look["lut"])
        shutil.copy(lut, work / ("look" + lut.suffix))
        vf.append(f"lut3d=look{lut.suffix}")
    for fx in edit.get("effects", []):  # short picture effects at moments (before graphics)
        a, d = float(fx["at"]), float(fx.get("dur", 0.3))
        en = f"enable='between(t,{a:.3f},{a + d:.3f})'"
        if fx["type"] == "glitch":  # RGB split + jitter blur
            amt = int(fx.get("amount", 14))
            vf.append(f"rgbashift=rh=-{amt}:bh={amt}:gv={amt // 3}:{en}")
            vf.append(f"gblur=sigma=2:{en}")
        elif fx["type"] == "blur_whip":  # quick directional blur, e.g. on a cut or a punch-in
            vf.append(f"gblur=sigma={float(fx.get('amount', 16))}:sigmaV=1:{en}")
    if vf:
        g.append(f"{cv}{','.join(vf)}[look]")
        cv, vf = "[look]", []
    for k, fx in enumerate(x for x in edit.get("effects", []) if x["type"] == "light_leak"):
        cv = light_leak(fx, k, cv, W, H, fps, total, work, inputs, g)
    for b in edit.get("backdrop", []):  # blur/dim the video behind a product card or title
        s0, s1 = float(b.get("start", 0)), float(b.get("end", total))
        en = f"enable='between(t,{s0},{s1})'"
        parts = []
        if b.get("blur", 18):
            parts.append(f"boxblur=luma_radius={int(b.get('blur', 18))}:luma_power=2:chroma_radius={int(b.get('blur', 18))}:{en}")
        if b.get("dim", 0.35):
            parts.append(f"drawbox=x=0:y=0:w=iw:h=ih:color=black@{float(b.get('dim', 0.35))}:t=fill:{en}")
        if parts:
            g.append(f"{cv}{','.join(parts)}[bd{len(g)}]")
            cv = f"[bd{len(g) - 1}]"
    if edit.get("frame"):  # video inside a rounded, bordered card on the brand background
        import cards
        bgp, maskp, bordp, (fm, ftop, fw, fh) = cards.frame_layers(edit, work)
        i0 = inputs.count("-i")
        for pth in (bgp, maskp, bordp):
            inputs += ["-loop", "1", "-framerate", str(fps), "-t", f"{total:.3f}", "-i", str(pth)]
        g.append(f"{cv}scale={fw}:{fh}:force_original_aspect_ratio=increase,crop={fw}:{fh},format=rgba[fv]")
        g.append(f"[{i0 + 1}:v]format=gray[fmk]")
        g.append("[fv][fmk]alphamerge[fva]")
        g.append(f"[{i0}:v]format=rgba[fbg]")
        g.append(f"[fbg][fva]overlay={fm}:{ftop}[fr1]")
        g.append(f"[fr1][{i0 + 2}:v]overlay=0:0,format=yuv420p[framed]")
        cv = "[framed]"
    for k, fr in enumerate(edit.get("frames", [])):  # timed "semi-frame": video shrinks into a rounded card over its own blurred copy
        from PIL import Image, ImageDraw
        s0, s1 = float(fr["start"]), float(fr["end"])
        sc = float(fr.get("scale", 0.84))
        fw, fh = int(W * sc) // 2 * 2, int(H * sc) // 2 * 2
        fx = int(W * float(fr["left"])) if "left" in fr else (W - fw) // 2
        fy = int(H * float(fr.get("top", (1 - sc) / 2)))
        rad = int(W * float(fr.get("radius", 0.05)))
        bwid = max(2, int(W * float(fr.get("border", 0.004))))
        mk = Image.new("L", (fw, fh), 0)
        ImageDraw.Draw(mk).rounded_rectangle([0, 0, fw - 1, fh - 1], rad, fill=255)
        mk.save(work / f"frm{k}_mask.png")
        bd = Image.new("RGBA", (fw + 2 * bwid, fh + 2 * bwid), (0, 0, 0, 0))
        bc = tuple(int(str(fr.get("border_color", "#FFFFFF")).lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
        ImageDraw.Draw(bd).rounded_rectangle([0, 0, fw + 2 * bwid - 1, fh + 2 * bwid - 1], rad + bwid,
                                             outline=bc + (int(255 * float(fr.get("border_alpha", 0.85))),), width=bwid)
        bd.save(work / f"frm{k}_border.png")
        i0 = inputs.count("-i")
        for pth in (work / f"frm{k}_mask.png", work / f"frm{k}_border.png"):
            inputs += ["-loop", "1", "-framerate", str(fps), "-t", f"{total:.3f}", "-i", str(pth)]
        blur = float(fr.get("blur", 34)) * W / 1080
        en = f"enable='between(t,{s0:.3f},{s1:.3f})'"
        bgmode = fr.get("bg", "lines")  # owner 2026-11-18: plain colour with soft lines, NOT blur
        if bgmode == "blur":
            g.append(f"{cv}split=3[frA{k}][frB{k}][frC{k}]")
            g.append(f"[frB{k}]scale={int(W * 1.15)}:-2,crop={W}:{H},gblur=sigma={blur:.1f},"
                     f"eq=brightness={float(fr.get('bg_brightness', -0.1))}:saturation=1.15[frbg{k}]")
        else:
            bgp = work / f"frm{k}_bg.png"
            frame_bg(fr, W, H, edit).save(bgp)
            ib = inputs.count("-i")
            inputs += ["-loop", "1", "-framerate", str(fps), "-t", f"{total:.3f}", "-i", str(bgp)]
            g.append(f"{cv}split=2[frA{k}][frC{k}]")
            g.append(f"[{ib}:v]format=rgba[frbg{k}]")
        g.append(f"[frC{k}]scale={fw}:{fh}:flags=lanczos,format=rgba[frfg{k}]")
        g.append(f"[{i0}:v]format=gray[frm{k}]")
        g.append(f"[frfg{k}][frm{k}]alphamerge[frfa{k}]")
        g.append(f"[frbg{k}][frfa{k}]overlay={fx}:{fy}[frc{k}]")
        g.append(f"[frc{k}][{i0 + 1}:v]overlay={fx - bwid}:{fy - bwid},format=yuv420p[frd{k}]")
        g.append(f"[frA{k}][frd{k}]overlay=0:0:{en}[fro{k}]")
        cv = f"[fro{k}]"
    for k, fl in enumerate(edit.get("flashes", [])):  # quick white (or any colour) flash, e.g. on cuts
        at, d = float(fl.get("at", fl) if isinstance(fl, dict) else fl), float(fl.get("dur", 0.18) if isinstance(fl, dict) else 0.18)
        a = float(fl.get("alpha", 0.75) if isinstance(fl, dict) else 0.75)
        col = "0x" + render_color(fl.get("color", "white") if isinstance(fl, dict) else "white")
        g.append(f"color=c={col}@{a}:s={W}x{H}:r={fps}:d={total:.3f},format=rgba,"
                 f"fade=t=in:st={max(0, at - 0.03):.3f}:d=0.03:alpha=1,fade=t=out:st={at:.3f}:d={d}:alpha=1[fl{k}]")
        g.append(f"{cv}[fl{k}]overlay=0:0:enable='between(t,{max(0, at - 0.03):.3f},{at + d:.3f})'[flo{k}]")
        cv = f"[flo{k}]"
    for k, gl in enumerate(edit.get("glass", [])):
        cv = glass_chain(gl, k, cv, W, H, fps, total, work, inputs, g)
    for j, ov in enumerate(edit.get("overlays", [])):
        idx = inputs.count("-i")
        img = overlay_image(edit, ov)
        if img.suffix.lower() == ".gif":  # animated: loop it for the whole video
            inputs += ["-stream_loop", "-1", "-t", f"{total:.3f}", "-i", str(img)]
        else:
            inputs += ["-loop", "1", "-framerate", str(fps), "-t", f"{total:.3f}", "-i", str(img)]
        g += overlay_chain(ov, idx, j, cv, W, H)
        cv = f"[ov{j}]"
    capc = edit.get("captions") or {}
    if capc and capc.get("style", {}).get("mode") == "html":
        import html_captions
        lines = load_json(edit["_dir"] / capc.get("file", "captions.json"))["lines"]
        lst = html_captions.build(edit, capc, lines, plan_kinetic(lines, capc), work / "htmlcaps", fps, total)
        idx = inputs.count("-i")
        inputs += ["-i", str(encode_layer(lst, fps, total))]
        g.append(f"[{idx}:v]fps={fps},format=rgba[hcap]")
        g.append(f"{cv}[hcap]overlay=0:0:eof_action=pass:format=auto[hcv]")
        cv = "[hcv]"
    if edit.get("cards"):  # full-frame brand cards (motion graphics inserts) over the picture
        import cards
        import html_captions
        lst = cards.build(edit, work / "cards", fps, total, html_captions.fonts(), lambda f: edl._src(edit["project"], f))
        idx = inputs.count("-i")
        inputs += ["-i", str(encode_layer(lst, fps, total))]
        g.append(f"[{idx}:v]fps={fps},format=rgba[cardl]")
        g.append(f"{cv}[cardl]overlay=0:0:eof_action=pass:format=auto[cardv]")
        cv = "[cardv]"
    pb = edit.get("progress_bar")
    if pb:
        hpx = int(pb.get("height", 10))
        y = 0 if pb.get("position", "top") == "top" else H - hpx
        col = "0x" + render_color(pb.get("color", "#FFE600"))
        g.append(f"color=c={col}:s={W}x{hpx}:r={fps}:d={total:.3f}[pbar]")
        g.append(f"{cv}[pbar]overlay=x='-{W}+{W}*t/{total:.3f}':y={y}:eval=frame[pb]")
        cv = "[pb]"
    if build_ass(edit, work / "overlay.ass"):
        fdir = work / "fonts"
        shutil.rmtree(fdir, ignore_errors=True)
        fdir.mkdir()
        for f in font_files():
            shutil.copy(f, fdir / f.name)
        vf.append("ass=overlay.ass:fontsdir=fonts")
    fade = edit.get("fade") or {}
    if fade.get("in"):
        vf.append(f"fade=t=in:st=0:d={fade['in']}")
    if fade.get("out"):
        vf.append(f"fade=t=out:st={total - fade['out']:.3f}:d={fade['out']}")
    if preview:
        vf.append(f"scale=-2:{min(640, o['height'])}")
    g.append(f"{cv}{','.join(vf) or 'null'}[vout]")

    # sound: music, ducking, fades, loudness
    music = edit.get("music")
    if music:
        midx = inputs.count("-i")
        inputs += ["-stream_loop", "-1", "-ss", f"{float(music.get('start', 0)):.3f}", "-i", str(resolve_music(edit, music))]
        m = (f"[{midx}:a]{AUDIO_FMT},atrim=duration={total:.3f},asetpts=PTS-STARTPTS,"
             f"volume={float(music.get('volume', 0.25))}")
        if music.get("fade_in"):
            m += f",afade=t=in:st=0:d={music['fade_in']}"
        if music.get("fade_out", 2):
            fo = float(music.get("fade_out", 2))
            m += f",afade=t=out:st={max(total - fo, 0):.3f}:d={fo}"
        g.append(m + "[mus]")
        if music.get("duck", True):
            g.append(f"{ca}asplit[voice][sc]")
            g.append("[mus][sc]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=500[musd]")
            g.append("[voice][musd]amix=inputs=2:duration=first:normalize=0[mix]")
        else:
            g.append(f"{ca}[mus]amix=inputs=2:duration=first:normalize=0[mix]")
        ca = "[mix]"
    sfx = list(edit.get("sfx") or [])
    cap = edit.get("captions") or {}
    csfx = cap.get("sfx") if cap else None
    if csfx:  # soft sound under every caption line (and optionally under each big word)
        lines = load_json(edit["_dir"] / cap.get("file", "captions.json"))["lines"]
        lines = [ln for ln in lines if any(w["text"] != "_" for w in ln.get("words") or [{"text": ln["text"]}])]
        for ln in lines:
            if csfx.get("line"):
                sfx.append({**csfx["line"], "at": ln["start"]})
        if csfx.get("big") and cap.get("style", {}).get("mode") == "kinetic":
            for ln, pick in zip(lines, plan_kinetic(lines, cap)):
                if pick is not None and pick > 0:
                    sfx.append({**csfx["big"], "at": ln["words"][pick]["start"]})
    if sfx:
        import sfx as sfxlib
        labels = []
        for j, fx in enumerate(sfx):
            at = float(fx.get("at", 0))
            if at >= total:
                continue
            path = edl._src(edit["project"], fx["file"]) if fx.get("file") else sfxlib.get(fx.get("sound", "whoosh"), edit.get("sfx_bank", ""))
            idx = inputs.count("-i")
            inputs += ["-i", str(path)]
            ms = int(at * 1000)
            g.append(f"[{idx}:a]{AUDIO_FMT},volume={float(fx.get('volume', 0.7))},adelay={ms}|{ms}[sfx{j}]")
            labels.append(f"[sfx{j}]")
        if labels:
            g.append(f"{ca}{''.join(labels)}amix=inputs={len(labels) + 1}:duration=first:normalize=0[withsfx]")
            ca = "[withsfx]"
    af = []
    if fade.get("in"):
        af.append(f"afade=t=in:st=0:d={fade['in']}")
    if fade.get("out"):
        af.append(f"afade=t=out:st={total - fade['out']:.3f}:d={fade['out']}")
    target = edit.get("loudness", -14)
    if target is not None:
        af.append(f"loudnorm=I={target}:TP=-1.5:LRA=11,{AUDIO_FMT}")
    g.append(f"{ca}{','.join(af) or 'anull'}[aout]")
    return inputs, ";\n".join(g), "[vout]", "[aout]"


def render_color(c: str) -> str:
    """RRGGBB hex for FFmpeg filters."""
    bgr = ass_color(c)[4:]
    return bgr[4:6] + bgr[2:4] + bgr[0:2]


POS9 = {"top-left": (0, 0), "top": (0.5, 0), "top-right": (1, 0), "left": (0, 0.5), "center": (0.5, 0.5),
        "right": (1, 0.5), "bottom-left": (0, 1), "bottom": (0.5, 1), "bottom-right": (1, 1)}


def overlay_image(edit: dict, ov: dict) -> Path:
    if ov.get("file"):
        return edl._src(edit["project"], ov["file"])
    cps = "_".join(f"{ord(ch):x}" for ch in ov["emoji"] if ord(ch) != 0xFE0F)
    ext = "gif" if ov.get("animated") else "png"
    dest = REPO / "assets" / "emoji" / f"{cps}.{ext}"
    if not dest.exists():
        import urllib.request
        dest.parent.mkdir(parents=True, exist_ok=True)
        url = f"https://fonts.gstatic.com/s/e/notoemoji/latest/{cps}/512.{ext}"
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                dest.write_bytes(r.read())
        except Exception as e:  # noqa: BLE001
            die(f"could not download emoji {ov['emoji']} ({e})")
    return dest


def overlay_chain(ov: dict, idx: int, j: int, base: str, W: int, H: int) -> list[str]:
    s0, s1 = float(ov["start"]), float(ov["end"])
    wo = max(2, int(W * float(ov.get("width", 0.18))) // 2 * 2)
    anim = ov.get("animation", "pop")
    u = f"(t-{s0})"
    if anim == "pop":
        f = f"if(lt({u},0.15),{u}/0.15*1.15,if(lt({u},0.3),1.15-({u}-0.15),1))"
        sc = f"scale=w='max(2,trunc({wo}*max(0.02,{f})/2)*2)':h=-2:eval=frame"
    else:
        sc = f"scale={wo}:-2"
    chain = f"[{idx}:v]format=rgba,{sc}"
    if anim not in ("none", "rise"):
        chain += f",fade=t=in:st={s0}:d=0.2:alpha=1"
    if anim != "none":
        chain += f",fade=t=out:st={max(s0, s1 - 0.25):.3f}:d=0.25:alpha=1"
    m = float(ov.get("margin", 0.06))
    if "x" in ov or "y" in ov:
        cx, cy = f"{W}*{float(ov.get('x', 0.5))}", f"{H}*{float(ov.get('y', 0.5))}"
    else:
        px, py = POS9[ov.get("position", "top-right")]
        cx = f"({W}*{m}+w/2)" if px == 0 else f"({W}-{W}*{m}-w/2)" if px == 1 else f"{W}/2"
        cy = f"({H}*{m * 1.5}+h/2)" if py == 0 else f"({H}-{H}*{m * 3}-h/2)" if py == 1 else f"{H}/2"
    dy = f"+{H * 0.08:.0f}*(1-clip({u}/0.3,0,1))" if anim == "slide_up" else ""
    if anim == "rise":  # comes up from the bottom edge with a little overshoot
        p = f"clip({u}/0.5,0,1)"
        ease = f"(1+2.4*pow({p}-1,3)+1.4*pow({p}-1,2))"
        dy = f"+({H}-({cy})+h/2+10)*(1-{ease})"
    return [chain + f"[img{j}]",
            f"{base}[img{j}]overlay=x='{cx}-w/2':y='{cy}-h/2{dy}':enable='between(t,{s0},{s1})':eval=frame[ov{j}]"]


def light_leak(fx: dict, k: int, cv: str, W: int, H: int, fps: int, total: float, work: Path, inputs: list, g: list) -> str:
    """Warm film light leak sweeping across the frame (screen-blended, fades in and out)."""
    import numpy as np
    from PIL import Image
    col = tuple(int(fx.get("color", "#FF9A3C").lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    w2 = W * 2
    yy, xx = np.mgrid[0:H, 0:w2]
    blob = np.zeros((H, w2))
    for cx, cy, r, a in ((0.35, 0.3, 0.5, 1.0), (0.55, 0.7, 0.4, .8), (0.7, 0.45, 0.3, .6)):
        blob += a * np.exp(-(((xx / w2 - cx) / (r / 2)) ** 2 + ((yy / H - cy) / r) ** 2))
    blob = np.clip(blob / blob.max(), 0, 1)
    alpha = (blob * 255 * float(fx.get("strength", 0.75))).astype("uint8")
    rgba = np.dstack([np.full((H, w2), c, "uint8") for c in col] + [alpha])
    path = work / f"leak{k}.png"
    Image.fromarray(rgba, "RGBA").save(path)
    a, d = float(fx["at"]), float(fx.get("dur", 0.8))
    idx = inputs.count("-i")
    inputs += ["-loop", "1", "-framerate", str(fps), "-t", f"{total:.3f}", "-i", str(path)]
    g.append(f"[{idx}:v]format=rgba,fade=t=in:st={a}:d={d * .3:.3f}:alpha=1,"
             f"fade=t=out:st={a + d * .55:.3f}:d={d * .45:.3f}:alpha=1[lk{k}]")
    g.append(f"{cv}[lk{k}]overlay=x='-{W}*clip((t-{a})/{d},0,1)':y=0:enable='between(t,{a},{a + d})':eval=frame[lo{k}]")
    return f"[lo{k}]"


def frame_bg(fr: dict, W: int, H: int, edit: dict):
    """Plain-colour background with soft lines for timed semi-frames: "lines" (diagonal pinstripes),
    "grid" (fine square grid) or "hlines" (horizontal ruled lines). Colour: bg_color (default brand bg2)."""
    from PIL import Image, ImageDraw
    if fr.get("bg") == "image":  # illustration / designed canvas behind the video window (cover-fit)
        im = Image.open(edl._src(edit["project"], fr["bg_file"])).convert("RGB")
        k = max(W / im.width, H / im.height)
        im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
        l, t = (im.width - W) // 2, (im.height - H) // 2
        return im.crop((l, t, l + W, t + H))
    if fr.get("bg") == "gradient":  # soft two-colour vertical gradient (e.g. the light-blue creator canvas)
        c1 = tuple(int(str(fr.get("bg_color", "#EAF7FD")).lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
        c2 = tuple(int(str(fr.get("bg_color2", "#9FDDF2")).lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
        im = Image.new("RGB", (W, H))
        d = ImageDraw.Draw(im)
        for y in range(H):
            u = y / H
            d.line([(0, y), (W, y)], fill=tuple(int(c1[i] + (c2[i] - c1[i]) * u) for i in range(3)))
        return im
    col = fr.get("bg_color") or (edit.get("brand") or {}).get("bg2") or "#0B2560"
    rgb = tuple(int(str(col).lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    lum = sum(rgb) / 3
    line = (255, 255, 255) if lum < 140 else (0, 0, 0)
    a = int(255 * float(fr.get("line_alpha", 0.07 if lum < 140 else 0.06)))
    im = Image.new("RGBA", (W, H), rgb + (255,))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    step = int(W * float(fr.get("line_step", 0.045)))
    lw = max(1, round(W / 1080 * float(fr.get("line_width", 2))))
    style = fr.get("bg", "lines")
    if style == "grid":
        for x in range(0, W, step):
            d.line([(x, 0), (x, H)], fill=line + (a,), width=lw)
        for y in range(0, H, step):
            d.line([(0, y), (W, y)], fill=line + (a,), width=lw)
    elif style == "hlines":
        for y in range(0, H, step):
            d.line([(0, y), (W, y)], fill=line + (a,), width=lw)
    else:  # diagonal pinstripes
        for x in range(-H, W, step):
            d.line([(x, H), (x + H, 0)], fill=line + (a,), width=lw)
    im = Image.alpha_composite(im, ov)
    # very soft radial light from the top so it isn't flat
    glow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(glow).ellipse([-W * 0.4, -H * 0.5, W * 1.4, H * 0.4], fill=26)
    from PIL import ImageFilter
    glow = glow.filter(ImageFilter.GaussianBlur(W * 0.3))
    im.paste(Image.new("RGBA", (W, H), (255, 255, 255, 255)), (0, 0), glow)
    return im.convert("RGB")


def glass_box(gl: dict, W: int, H: int) -> tuple[int, int, int, int]:
    bw = int(W * float(gl.get("w", 0.6))) // 2 * 2
    bh = int(H * float(gl.get("h", 0.1))) // 2 * 2
    x0 = int(W * float(gl.get("x", 0.5)) - bw / 2)
    y0 = int(H * float(gl.get("y", 0.5)) - bh / 2)
    return max(0, min(x0, W - bw)), max(0, min(y0, H - bh)), bw, bh


def glass_chain(gl: dict, k: int, cv: str, W: int, H: int, fps: int, total: float, work: Path,
                inputs: list, g: list) -> str:
    """Liquid-glass card: blurred, brightened video inside a rounded rectangle with a light
    tint, top highlight, thin white border and soft shadow (PNG layers made with Pillow)."""
    import numpy as np
    from PIL import Image, ImageDraw, ImageFilter
    x0, y0, bw, bh = glass_box(gl, W, H)
    s0, s1 = float(gl.get("start", 0)), float(gl.get("end", total))
    rad = int(min(bw, bh) * float(gl.get("radius", 0.28)))
    ss = 4  # supersampling for smooth corners
    big = Image.new("L", (bw * ss, bh * ss), 0)
    ImageDraw.Draw(big).rounded_rectangle((0, 0, bw * ss - 1, bh * ss - 1), rad * ss, fill=255)
    mask = big.resize((bw, bh), Image.LANCZOS)
    mask.save(work / f"glass{k}_mask.png")
    tc = tuple(int(gl.get("tint_color", "#FFFFFF").lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    bc = tuple(int(gl.get("border_color", "#FFFFFF").lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    face = Image.new("RGBA", (bw, bh), tc + (int(255 * float(gl.get("tint", 0.10))),))
    hl = Image.new("L", (bw, bh), 0)
    for y in range(int(bh * 0.5)):
        ImageDraw.Draw(hl).line((0, y, bw, y), fill=int(70 * (1 - y / (bh * 0.5))))
    face.putalpha(Image.fromarray(np.minimum(np.array(face.split()[-1]).astype(int) + np.array(hl).astype(int), 255).astype("uint8")))
    bd = Image.new("RGBA", (bw * ss, bh * ss), (0, 0, 0, 0))
    ImageDraw.Draw(bd).rounded_rectangle((ss, ss, bw * ss - ss - 1, bh * ss - ss - 1), rad * ss,
                                         outline=bc + (int(255 * float(gl.get("border", 0.55))),), width=max(1, round(float(gl.get("border_width", 2)) * W / 1080)) * ss)
    face.alpha_composite(bd.resize((bw, bh), Image.LANCZOS))
    if gl.get("crystal"):  # crystal-clear glass: no frost, specular sheen, bright rim + dark outer edge
        cr = Image.new("RGBA", (bw * ss, bh * ss), (0, 0, 0, 0))
        dr = ImageDraw.Draw(cr)
        lw = max(1, round(W / 1080 * 1.5)) * ss
        dr.rounded_rectangle((0, 0, bw * ss - 1, bh * ss - 1), rad * ss, outline=(0, 0, 0, 70), width=lw)  # edge definition
        ins = int(lw * 3.2)
        dr.rounded_rectangle((ins, ins, bw * ss - ins - 1, bh * ss - ins - 1), max(1, rad * ss - ins), outline=(255, 255, 255, 95), width=lw)
        cr = cr.resize((bw, bh), Image.LANCZOS)
        sheen = Image.new("L", (bw, bh), 0)
        sd = ImageDraw.Draw(sheen)
        sd.polygon([(bw * 0.08, 0), (bw * 0.30, 0), (bw * 0.12, bh), (-bw * 0.10, bh)], fill=55)  # diagonal streak
        sd.polygon([(bw * 0.36, 0), (bw * 0.42, 0), (bw * 0.24, bh), (bw * 0.18, bh)], fill=35)
        sheen = sheen.filter(ImageFilter.GaussianBlur(max(2, bw * 0.012)))
        top = Image.new("L", (bw, bh), 0)
        for y in range(int(bh * 0.18)):
            ImageDraw.Draw(top).line((0, y, bw, y), fill=int(90 * (1 - y / (bh * 0.18)) ** 2))
        lum = Image.fromarray(np.minimum(np.array(sheen).astype(int) + np.array(top).astype(int), 255).astype("uint8"))
        spec = Image.new("RGBA", (bw, bh), (255, 255, 255, 0))
        spec.putalpha(lum)
        face.alpha_composite(spec)
        face.alpha_composite(cr)
    clear = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    face = Image.composite(face, clear, mask)
    face.save(work / f"glass{k}_face.png")
    pad = 40
    sh = Image.new("RGBA", (bw + 2 * pad, bh + 2 * pad), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((pad, pad + 10, pad + bw, pad + bh + 10), rad, fill=(0, 0, 0, 110))
    sh.filter(ImageFilter.GaussianBlur(18)).save(work / f"glass{k}_shadow.png")

    idx = inputs.count("-i")
    for name in ("mask", "face", "shadow"):
        inputs += ["-loop", "1", "-framerate", str(fps), "-t", f"{total:.3f}", "-i", f"glass{k}_{name}.png"]
    fade = f"fade=t=in:st={s0}:d=0.25:alpha=1,fade=t=out:st={max(s0, s1 - 0.25):.3f}:d=0.25:alpha=1"
    en = f"enable='between(t,{s0},{s1})'"
    blur = float(gl.get("blur", 22)) * W / 1080  # same look at 1080p and 4K
    if gl.get("crystal"):  # clear lens: tiny magnification (refraction), almost no blur
        mg = float(gl.get("magnify", 1.06))
        cw, ch = int(bw / mg) // 2 * 2, int(bh / mg) // 2 * 2
        cx0, cy0 = x0 + (bw - cw) // 2, y0 + (bh - ch) // 2
        g.append(f"{cv}split[ga{k}][gb{k}]")
        g.append(f"[gb{k}]crop={cw}:{ch}:{cx0}:{cy0},scale={bw}:{bh}:flags=lanczos,gblur=sigma={float(gl.get('blur', 0.8)) * W / 1080:.2f},"
                 f"eq=brightness={float(gl.get('brightness', 0.03))}:saturation={float(gl.get('saturation', 1.05))},format=rgba[gbl{k}]")
    else:
        g.append(f"{cv}split[ga{k}][gb{k}]")
        g.append(f"[gb{k}]crop={bw}:{bh}:{x0}:{y0},gblur=sigma={blur},eq=brightness={float(gl.get("brightness", 0.05))}:saturation={float(gl.get("saturation", 1.3))},format=rgba[gbl{k}]")
    g.append(f"[{idx}:v]format=gray[gm{k}]")
    g.append(f"[gbl{k}][gm{k}]alphamerge,{fade}[gg{k}]")
    g.append(f"[{idx + 2}:v]format=rgba,{fade}[gs{k}]")
    g.append(f"[{idx + 1}:v]format=rgba,{fade}[gf{k}]")
    g.append(f"[ga{k}][gs{k}]overlay={x0 - pad}:{y0 - pad}:{en}[g1{k}]")
    g.append(f"[g1{k}][gg{k}]overlay={x0}:{y0}:{en}[g2{k}]")
    g.append(f"[g2{k}][gf{k}]overlay={x0}:{y0}:{en}[g3{k}]")
    return f"[g3{k}]"


def resolve_music(edit: dict, music: dict) -> Path:
    return edl._src(edit["project"], music.get("file") or die("music needs a \"file\""))


def render_to(edit: dict, dest: Path, preview: bool, work: Path) -> None:
    work.mkdir(parents=True, exist_ok=True)
    inputs, graph, vout, aout = build_graph(edit, work, preview)
    (work / "graph.txt").write_text(graph, encoding="utf-8")
    q = edit.get("quality", {})
    enc = (["-c:v", "libx264", "-preset", "veryfast", "-crf", "28"] if preview else
           ["-c:v", "libx264", "-preset", q.get("preset", "medium"), "-crf", str(q.get("crf", 18))])
    cmd = (["ffmpeg", "-hide_banner", "-y"] + inputs +
           ["-filter_complex", graph, "-map", vout, "-map", aout] + enc +
           ["-pix_fmt", "yuv420p", "-r", str(edit["output"]["fps"]), "-c:a", "aac", "-b:a", "192k",
            "-t", f"{edit['_total']:.3f}", "-movflags", "+faststart", os.path.abspath(dest)])
    run(cmd, cwd=work)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("edit")
    ap.add_argument("--preview", action="store_true", help="fast low-resolution render for checking")
    ap.add_argument("--out", help="output file (default Export/<project>/<project>.mp4)")
    args = ap.parse_args()
    need("ffmpeg")

    edit = edl.load(resolve(args.edit))
    name = edit["project"] + ("_preview" if args.preview else "")
    dest = resolve(args.out) if args.out else edit["_dir"] / f"{name}.mp4"
    print(f"Rendering {len(edit['shots'])} shots, {fmt_time(edit['_total'])} -> {dest.relative_to(REPO) if dest.is_relative_to(REPO) else dest}")
    t0 = time.time()
    render_to(edit, dest, args.preview, edit["_dir"] / "work" / "render")
    print(f"Done in {time.time() - t0:.0f}s: {dest} ({dest.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
