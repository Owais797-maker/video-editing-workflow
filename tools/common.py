"""Shared helpers for the video editing tools (standard library only)."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EDITS = REPO / "Video Edits"
FONTS = REPO / "fonts"
FONT_EXT = {".ttf", ".otf", ".ttc"}
VIDEO_EXT = {".mp4", ".mov", ".mkv", ".avi", ".m4v", ".webm", ".mts", ".3gp"}


def die(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def need(tool: str) -> str:
    path = shutil.which(tool)
    if not path:
        die(f"'{tool}' not found. Install FFmpeg and make sure it is on PATH (run tools/check_setup.py).")
    return path


def run(cmd: list[str], cwd: Path | None = None, quiet: bool = True) -> subprocess.CompletedProcess:
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        tail = "\n".join(proc.stderr.strip().splitlines()[-25:])
        die(f"command failed: {' '.join(map(str, cmd[:6]))} ...\n{tail}")
    if not quiet:
        print(proc.stderr)
    return proc


def resolve(p: str | Path) -> Path:
    """Paths in edit.json are relative to the repository root."""
    p = Path(p)
    return p if p.is_absolute() else (REPO / p)


def probe(path: Path) -> dict:
    need("ffprobe")
    if not path.exists():
        die(f"file not found: {path}")
    out = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)]).stdout
    data = json.loads(out)
    v = next((s for s in data["streams"] if s.get("codec_type") == "video"), None)
    a = next((s for s in data["streams"] if s.get("codec_type") == "audio"), None)
    info = {"path": str(path), "duration": float(data["format"].get("duration", 0) or 0), "has_audio": a is not None}
    if v:
        w, h = int(v.get("width", 0)), int(v.get("height", 0))
        rot = 0
        for sd in v.get("side_data_list", []) or []:
            if "rotation" in sd:
                rot = abs(int(sd["rotation"]))
        rot = rot or abs(int((v.get("tags") or {}).get("rotate", 0) or 0))
        if rot in (90, 270):
            w, h = h, w
        num, _, den = (v.get("avg_frame_rate") or "0/1").partition("/")
        fps = float(num) / float(den or 1) if float(den or 1) else 0.0
        info.update(width=w, height=h, fps=round(fps, 3), vcodec=v.get("codec_name"))
    if a:
        info.update(acodec=a.get("codec_name"), sample_rate=int(a.get("sample_rate", 0) or 0))
    return info


def fmt_time(t: float) -> str:
    m, s = divmod(max(t, 0.0), 60)
    return f"{int(m)}:{s:04.1f}"


def file_key(path: Path) -> str:
    """Stable cache name for a source file (stem + short hash of its repo-relative path)."""
    try:
        rel = path.resolve().relative_to(REPO).as_posix()
    except ValueError:
        rel = path.resolve().as_posix()
    return f"{path.stem}-{hashlib.sha1(rel.encode()).hexdigest()[:6]}"


def font_files() -> list[Path]:
    return sorted(p for p in FONTS.rglob("*") if p.suffix.lower() in FONT_EXT)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        die(f"file not found: {path}")
    except json.JSONDecodeError as e:
        die(f"{path} is not valid JSON: {e}")


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def encode_layer(ffconcat: Path, fps: int, total: float) -> Path:
    """Turn an ffconcat list of transparent PNGs into one light alpha video (QuickTime RLE)."""
    out = ffconcat.with_suffix(".mov")
    run(["ffmpeg", "-hide_banner", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(ffconcat),
         "-vf", f"fps={fps},format=argb", "-t", f"{total:.3f}", "-c:v", "qtrle", str(out)])
    return out
