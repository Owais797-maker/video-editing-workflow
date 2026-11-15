#!/usr/bin/env python3
"""Analyse a video so Claude can study its editing style or its content.

    python tools/analyze.py "Video Edits/Reference/my-reel/inspo.mp4" --project my-reel

Writes to Video Edits/Export/<project>/work/analysis/<video>/ :
    analysis.json   size, fps, duration, every cut, shot-length stats, loudness
    analysis.md     the same as a readable report
    shot_###.jpg    one frame per shot (more for long shots)
    sheet.jpg       contact sheet of all those frames
"""
import argparse
import re
import statistics
from pathlib import Path

from common import EDITS, REPO, die, file_key, fmt_time, need, probe, resolve, run, save_json

MAX_FRAMES = 60


def detect_cuts(path: Path, threshold: float) -> list[float]:
    proc = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-an",
                "-vf", f"scale=320:-2,select='gt(scene,{threshold})',showinfo", "-f", "null", "-"])
    return [float(m) for m in re.findall(r"pts_time:([0-9.]+)", proc.stderr)]


def loudness(path: Path) -> float | None:
    proc = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-vn",
                "-af", "ebur128=framelog=quiet", "-f", "null", "-"])
    m = re.findall(r"I:\s+(-?[0-9.]+) LUFS", proc.stderr)
    return float(m[-1]) if m else None


def frame_times(shots: list[tuple[float, float]], interval: float) -> list[tuple[int, float]]:
    """(shot index, time) pairs: shot midpoints, plus every `interval` s inside long shots."""
    pts = []
    for i, (a, b) in enumerate(shots):
        n = max(1, int((b - a) // interval))
        pts += [(i, a + (b - a) * (k + 0.5) / n) for k in range(n)]
    if len(pts) > MAX_FRAMES:  # keep an even spread
        step = len(pts) / MAX_FRAMES
        pts = [pts[int(k * step)] for k in range(MAX_FRAMES)]
    return pts


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--project", help="project name (output goes to its work folder)")
    ap.add_argument("--out", help="output folder (overrides --project)")
    ap.add_argument("--threshold", type=float, default=0.3, help="cut sensitivity 0-1, lower finds more cuts (default 0.3)")
    ap.add_argument("--interval", type=float, default=8.0, help="extra frame every N s inside long shots (default 8)")
    args = ap.parse_args()
    need("ffmpeg")

    src = resolve(args.video)
    info = probe(src)
    if "width" not in info:
        die(f"{src} has no video stream")
    if args.out:
        out = resolve(args.out)
    elif args.project:
        out = EDITS / "Export" / args.project / "work" / "analysis" / file_key(src)
    else:
        die("pass --project <name> or --out <folder>")
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("shot_*.jpg"):
        old.unlink()

    dur = info["duration"]
    cuts = [t for t in detect_cuts(src, args.threshold) if 0.15 < t < dur - 0.15]
    bounds = [0.0] + cuts + [dur]
    shots = [(a, b) for a, b in zip(bounds, bounds[1:]) if b - a > 0.04]
    lengths = [b - a for a, b in shots]

    frames = frame_times(shots, args.interval)
    for k, (_, t) in enumerate(frames, 1):
        run(["ffmpeg", "-hide_banner", "-y", "-ss", f"{t:.3f}", "-i", str(src), "-frames:v", "1",
             "-vf", "scale=360:-2", "-q:v", "4", str(out / f"shot_{k:03d}.jpg")])
    cols = 6 if info["width"] <= info["height"] else 4
    rows = -(-len(frames) // cols)
    run(["ffmpeg", "-hide_banner", "-y", "-i", str(out / "shot_%03d.jpg"), "-frames:v", "1",
         "-vf", f"scale=240:-2,tile={cols}x{rows}:padding=4:color=black", "-q:v", "4", str(out / "sheet.jpg")])

    lufs = loudness(src) if info["has_audio"] else None
    stats = {
        "shots": len(shots),
        "avg_shot": round(statistics.mean(lengths), 2),
        "median_shot": round(statistics.median(lengths), 2),
        "min_shot": round(min(lengths), 2),
        "max_shot": round(max(lengths), 2),
        "cuts_per_minute": round(len(cuts) / dur * 60, 1) if dur else 0,
    }
    result = {
        "source": src.relative_to(REPO).as_posix() if src.is_relative_to(REPO) else str(src),
        "info": info, "stats": stats, "loudness_lufs": lufs,
        "shots": [{"n": i + 1, "start": round(a, 2), "end": round(b, 2), "length": round(b - a, 2)} for i, (a, b) in enumerate(shots)],
        "frames": [{"file": f"shot_{k:03d}.jpg", "shot": i + 1, "time": round(t, 2)} for k, (i, t) in enumerate(frames, 1)],
    }
    save_json(out / "analysis.json", result)

    orient = "vertical 9:16-ish" if info["height"] > info["width"] else "horizontal" if info["width"] > info["height"] else "square"
    md = [f"# Analysis: {src.name}", "",
          f"- **Format:** {info['width']}x{info['height']} ({orient}), {info['fps']} fps, {fmt_time(dur)} long",
          f"- **Audio:** {'yes' if info['has_audio'] else 'none'}" + (f", loudness {lufs} LUFS" if lufs is not None else ""),
          f"- **Shots:** {stats['shots']} (cut threshold {args.threshold}), {stats['cuts_per_minute']} cuts/min",
          f"- **Shot length:** avg {stats['avg_shot']}s, median {stats['median_shot']}s, range {stats['min_shot']}–{stats['max_shot']}s",
          "", "![contact sheet](sheet.jpg)", "", "| Shot | Start | End | Length |", "|---|---|---|---|"]
    md += [f"| {s['n']} | {fmt_time(s['start'])} | {fmt_time(s['end'])} | {s['length']}s |" for s in result["shots"]]
    md += ["", "Frames: " + ", ".join(f"`{f['file']}` (shot {f['shot']} @ {fmt_time(f['time'])})" for f in result["frames"])]
    (out / "analysis.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"{src.name}: {stats['shots']} shots, avg {stats['avg_shot']}s, {stats['cuts_per_minute']} cuts/min")
    print(f"Report: {(out / 'analysis.md').relative_to(REPO)}")
    print(f"Contact sheet: {(out / 'sheet.jpg').relative_to(REPO)}")


if __name__ == "__main__":
    main()
