#!/usr/bin/env python3
"""Make a storyboard from edit.json for approval before rendering.

    python tools/storyboard.py "Video Edits/Export/my-reel/edit.json"

Writes Export/<project>/storyboard.md and storyboard/ (one frame per shot plus
overview.jpg). The frames are taken from a quick preview render, so they show
exactly what the final video will look like (text, captions, stickers, motion).
"""
import argparse
import shutil

import edl
import render
from common import REPO, fmt_time, load_json, resolve, run


def frame_at(video, t: float, dest) -> None:
    run(["ffmpeg", "-hide_banner", "-y", "-ss", f"{t:.3f}", "-i", str(video), "-frames:v", "1",
         "-vf", "scale=-2:480", "-q:v", "3", str(dest)])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("edit")
    edit = edl.load(resolve(ap.parse_args().edit))
    d = edit["_dir"]
    sb = d / "storyboard"
    shutil.rmtree(sb, ignore_errors=True)
    sb.mkdir(parents=True)
    work = d / "work" / "storyboard"
    preview = work / "preview.mp4"
    print("Rendering a quick preview for the storyboard frames ...")
    render.render_to(edit, preview, True, work)

    cap_lines = []
    if edit.get("captions"):
        cap_lines = load_json(d / edit["captions"].get("file", "captions.json"))["lines"]

    o, total = edit["output"], edit["_total"]
    md = [f"# Storyboard: {edit.get('title', edit['project'])}", "",
          f"**Output:** {o['width']}x{o['height']}, {o['fps']} fps, **{fmt_time(total)}** long, "
          f"{len(edit['shots'])} shots, framing: {o['fit']}", ""]
    if edit.get("summary"):
        md += [edit["summary"], ""]
    if edit.get("reference_notes"):
        md += ["## Style taken from the reference", "", edit["reference_notes"], ""]
    md += ["![overview](storyboard/overview.jpg)", "", "## Shots", ""]

    for s in edit["shots"]:
        a, b = s["_start"], s["_start"] + s["_len"]
        frame = sb / f"shot_{s['_n']:02d}.jpg"
        frame_at(preview, a + s["_len"] * float(s.get("frame_at", 0.5)), frame)
        extras = []
        if s["speed"] != 1:
            extras.append(f"speed {s['speed']}x")
        if s.get("zoom", 1) != 1:
            extras.append(f"zoom {s['zoom']}x")
        if s.get("mute"):
            extras.append("muted")
        texts = [x["text"].replace("\n", " / ") for x in edit["texts"] if x.get("start", 0) < b and x["end"] > a]
        caps = [ln["text"] for ln in cap_lines if a <= ln["start"] < b]
        tr = s["transition"]
        md += [f"### {s['_n']}. {fmt_time(a)} – {fmt_time(b)} ({s['_len']:.1f}s)", "",
               f"<img src=\"storyboard/{frame.name}\" height=\"320\">", "",
               f"- **Clip:** `{s['src']}` {fmt_time(s['in'])}–{fmt_time(s['out'])}" + (f" ({', '.join(extras)})" if extras else "")]
        if s.get("description"):
            md.append(f"- **What happens:** {s['description']}")
        if texts:
            md.append(f"- **On-screen text:** {' | '.join(texts)}")
        if caps:
            md.append(f"- **Captions:** {' / '.join(caps)}")
        if s is not edit["shots"][-1]:
            how = "hard cut" if tr["type"] == "cut" else f"{tr['type']} transition ({tr['duration']}s)"
            md.append(f"- **Then:** {how}")
        md.append("")

    audio = []
    if edit.get("music"):
        m = edit["music"]
        audio.append(f"- Music: `{m['file']}` at volume {m.get('volume', 0.25)}" +
                     (", dips under speech" if m.get("duck", True) else ""))
    if any(not s.get("mute") and s["_info"]["has_audio"] for s in edit["shots"]):
        audio.append("- Original sound from the clips is kept (except muted shots)")
    if edit.get("loudness", -14) is not None:
        audio.append(f"- Loudness normalised to {edit.get('loudness', -14)} LUFS")
    if audio:
        md += ["## Audio", ""] + audio + [""]
    md += ["## Approval", "", "Reply **OK** to render, or list changes by shot number (e.g. \"shot 3 shorter, bigger text\")."]
    (d / "storyboard.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    n = len(edit["shots"])
    cols = min(n, 6)
    run(["ffmpeg", "-hide_banner", "-y", "-i", str(sb / "shot_%02d.jpg"), "-frames:v", "1",
         "-vf", f"scale=-2:360,tile={cols}x{-(-n // cols)}:padding=6:color=white", "-q:v", "3", str(sb / "overview.jpg")])
    print(f"Storyboard: {(d / 'storyboard.md').relative_to(REPO)}  ({n} shots, {fmt_time(total)})")
    print(f"Overview image: {(sb / 'overview.jpg').relative_to(REPO)}")


if __name__ == "__main__":
    main()
