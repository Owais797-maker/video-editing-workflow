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
    return ("Style: {n},{font},{size},{pc},{sc},{oc},{bc},{bold},0,0,0,100,100,0,0,{bs},{ol},{sh},{al},60,60,{mv},1"
            .format(n=name, font=st.get("font", "DejaVu Sans"), size=size,
                    pc=ass_color(st.get("color", "white")), sc=ass_color(st.get("color", "white")),
                    oc=ass_color(st.get("box_color", "black"), 0x40) if box else ass_color(st.get("outline_color", "black")),
                    bc=ass_color("#000000", 0x80), bold=-1 if st.get("bold", True) else 0,
                    bs=3 if box else 1, ol=round(size * outline / 10, 1) if not box else round(size * 0.25),
                    sh=st.get("shadow", 0), al=align, mv=int(H * float(st.get("margin", 12)) / 100)))


def build_ass(edit: dict, path: Path) -> bool:
    W, H = edit["output"]["width"], edit["output"]["height"]
    styles, events = [], []
    for i, x in enumerate(edit["texts"]):
        name = f"T{i}"
        styles.append(style_line(name, x, H, 5.0, edl.POSITIONS[x["position"]]))
        anim = x.get("animation", "fade")
        fx = "{\\fad(200,200)}" if anim == "fade" else "{\\fad(0,0)\\t(0,180,\\fscx112\\fscy112)\\t(180,320,\\fscx100\\fscy100)}" if anim == "pop" else ""
        events.append(f"Dialogue: 1,{ass_time(x.get('start', 0))},{ass_time(x['end'])},{name},,0,0,0,,{fx}{ass_text(x['text'])}")

    cap = edit.get("captions")
    if cap:
        cfile = edit["_dir"] / cap.get("file", "captions.json")
        if not cfile.exists():
            die(f"{cfile.relative_to(REPO)} not found. Run: python tools/captions.py \"{edit['_path'].relative_to(REPO).as_posix()}\"")
        st = cap.get("style", {})
        styles.append(style_line("Cap", st, H, 4.2, edl.POSITIONS[st.get("position", "bottom")]))
        hi = st.get("highlight_color")
        upper = st.get("uppercase", False)
        for ln in load_json(cfile)["lines"]:
            text = ln["text"].upper() if upper else ln["text"]
            words = ln.get("words") or []
            if hi and words and " ".join(w["text"] for w in words) == ln["text"]:
                # one event per spoken word, with that word highlighted
                for k, w in enumerate(words):
                    a = w["start"] if k else ln["start"]
                    b = words[k + 1]["start"] if k + 1 < len(words) else ln["end"]
                    parts = [(p.upper() if upper else p) for p in (x["text"] for x in words)]
                    parts[k] = "{\\c" + ass_color(hi) + "}" + ass_text(parts[k]) + "{\\r}"
                    body = " ".join(p if j == k else ass_text(p) for j, p in enumerate(parts))
                    events.append(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},Cap,,0,0,0,,{body}")
            else:
                events.append(f"Dialogue: 0,{ass_time(ln['start'])},{ass_time(ln['end'])},Cap,,0,0,0,,{ass_text(text)}")
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
        g.append(f"[f{n}]fps={fps},format=yuv420p,trim=duration={L:.3f},setpts=PTS-STARTPTS,settb=AVTB[v{n}]")
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

    # picture: look, text overlay, fades, preview scale
    vf = []
    look = edit.get("look") or {}
    if any(k in look for k in ("brightness", "contrast", "saturation", "gamma")):
        vf.append("eq=" + ":".join(f"{k}={look[k]}" for k in ("brightness", "contrast", "saturation", "gamma") if k in look))
    if look.get("lut"):
        lut = resolve(look["lut"])
        shutil.copy(lut, work / ("look" + lut.suffix))
        vf.append(f"lut3d=look{lut.suffix}")
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


def resolve_music(edit: dict, music: dict) -> Path:
    return edl._src(edit["project"], music.get("file") or die("music needs a \"file\""))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("edit")
    ap.add_argument("--preview", action="store_true", help="fast low-resolution render for checking")
    ap.add_argument("--out", help="output file (default Export/<project>/<project>.mp4)")
    args = ap.parse_args()
    need("ffmpeg")

    edit = edl.load(resolve(args.edit))
    work = edit["_dir"] / "work" / "render"
    work.mkdir(parents=True, exist_ok=True)
    inputs, graph, vout, aout = build_graph(edit, work, args.preview)
    (work / "graph.txt").write_text(graph, encoding="utf-8")

    name = edit["project"] + ("_preview" if args.preview else "")
    dest = resolve(args.out) if args.out else edit["_dir"] / f"{name}.mp4"
    q = edit.get("quality", {})
    enc = (["-c:v", "libx264", "-preset", "veryfast", "-crf", "28"] if args.preview else
           ["-c:v", "libx264", "-preset", q.get("preset", "medium"), "-crf", str(q.get("crf", 18))])
    cmd = (["ffmpeg", "-hide_banner", "-y"] + inputs +
           ["-filter_complex", graph, "-map", vout, "-map", aout] + enc +
           ["-pix_fmt", "yuv420p", "-r", str(edit["output"]["fps"]), "-c:a", "aac", "-b:a", "192k",
            "-t", f"{edit['_total']:.3f}", "-movflags", "+faststart", os.path.abspath(dest)])
    print(f"Rendering {len(edit['shots'])} shots, {fmt_time(edit['_total'])} -> {dest.relative_to(REPO) if dest.is_relative_to(REPO) else dest}")
    t0 = time.time()
    run(cmd, cwd=work)
    print(f"Done in {time.time() - t0:.0f}s: {dest}")


if __name__ == "__main__":
    main()
