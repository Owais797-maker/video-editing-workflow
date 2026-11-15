#!/usr/bin/env python3
"""Render the final video from an approved edit.json.

    python tools/render.py "Video Edits/Export/my-reel/edit.json" --preview   # fast, small check
    python tools/render.py "Video Edits/Export/my-reel/edit.json"             # full quality

Output: Export/<project>/<project>.mp4 (or <project>_preview.mp4).
"""
from __future__ import annotations

import argparse
import os
import shutil
import time
from pathlib import Path

import edl
from common import REPO, die, font_files, fmt_time, load_json, need, resolve, run

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
                    oc=ass_color(st.get("box_color", "black"), 0x40) if box else ass_color(st.get("outline_color", "black")),
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
        text = sg["text"].upper() if sg.get("uppercase") else sg["text"].lower() if sg.get("lowercase") else sg["text"]
        sep = "" if i == 0 else ("\\N" if sg.get("newline") else " ")
        out.append(f"{sep}{{{tags}}}{ass_text(text)}")
    return "".join(out)


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
        styles.append(style_line(name, x, H, 5.0, edl.POSITIONS[x["position"]]))
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
        pop = "{" + pos + anim + "}" if pos or anim else ""
        keep = "{" + pos + "}" if pos else ""
        for ln in load_json(cfile)["lines"]:
            text = case(ln["text"])
            words = ln.get("words") or []
            if hi and words and " ".join(w["text"] for w in words) == ln["text"]:
                # one event per spoken word, with that word highlighted
                parts = [ass_text(case(w["text"])) for w in words]
                for k, w in enumerate(words):
                    a = w["start"] if k else ln["start"]
                    b = words[k + 1]["start"] if k + 1 < len(words) else ln["end"]
                    big = f"\\fscx{hscale}\\fscy{hscale}" if hscale != 100 else ""
                    shown = list(parts)
                    shown[k] = "{\\c" + ass_color(hi) + big + "}" + parts[k] + "{\\r}"
                    events.append(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},Cap,,0,0,0,,{pop if k == 0 else keep}{' '.join(shown)}")
            else:
                events.append(f"Dialogue: 0,{ass_time(ln['start'])},{ass_time(ln['end'])},Cap,,0,0,0,,{pop}{ass_text(text)}")
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
    if look.get("lut"):
        lut = resolve(look["lut"])
        shutil.copy(lut, work / ("look" + lut.suffix))
        vf.append(f"lut3d=look{lut.suffix}")
    if vf:
        g.append(f"{cv}{','.join(vf)}[look]")
        cv, vf = "[look]", []
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
    for j, ov in enumerate(edit.get("overlays", [])):
        idx = inputs.count("-i")
        img = overlay_image(edit, ov)
        if img.suffix.lower() == ".gif":  # animated: loop it for the whole video
            inputs += ["-stream_loop", "-1", "-t", f"{total:.3f}", "-i", str(img)]
        else:
            inputs += ["-loop", "1", "-framerate", str(fps), "-t", f"{total:.3f}", "-i", str(img)]
        g += overlay_chain(ov, idx, j, cv, W, H)
        cv = f"[ov{j}]"
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
    sfx = edit.get("sfx") or []
    if sfx:
        import sfx as sfxlib
        labels = []
        for j, fx in enumerate(sfx):
            at = float(fx.get("at", 0))
            if at >= total:
                continue
            path = edl._src(edit["project"], fx["file"]) if fx.get("file") else sfxlib.get(fx.get("sound", "whoosh"))
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
    if anim != "none":
        chain += f",fade=t=in:st={s0}:d=0.2:alpha=1,fade=t=out:st={max(s0, s1 - 0.25):.3f}:d=0.25:alpha=1"
    m = float(ov.get("margin", 0.06))
    if "x" in ov or "y" in ov:
        cx, cy = f"{W}*{float(ov.get('x', 0.5))}", f"{H}*{float(ov.get('y', 0.5))}"
    else:
        px, py = POS9[ov.get("position", "top-right")]
        cx = f"({W}*{m}+w/2)" if px == 0 else f"({W}-{W}*{m}-w/2)" if px == 1 else f"{W}/2"
        cy = f"({H}*{m * 1.5}+h/2)" if py == 0 else f"({H}-{H}*{m * 3}-h/2)" if py == 1 else f"{H}/2"
    dy = f"+{H * 0.08:.0f}*(1-clip({u}/0.3,0,1))" if anim == "slide_up" else ""
    return [chain + f"[img{j}]",
            f"{base}[img{j}]overlay=x='{cx}-w/2':y='{cy}-h/2{dy}':enable='between(t,{s0},{s1})':eval=frame[ov{j}]"]


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
