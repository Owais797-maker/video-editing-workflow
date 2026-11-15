"""Load and validate an edit.json (the edit decision list) and work out its timeline.

Shared by captions.py, storyboard.py and render.py, so the storyboard always
shows exactly what render.py will produce. The format is documented in
tools/EDIT_FORMAT.md.
"""
from __future__ import annotations

from pathlib import Path

from common import EDITS, REPO, die, load_json, probe

FITS = {"crop", "blur", "pad"}
POSITIONS = {"top": 8, "center": 5, "bottom": 2}


def _src(project: str, name: str) -> Path:
    for base in (EDITS / "Raw" / project, EDITS / "Reference" / project, REPO):
        p = base / name
        if p.exists():
            return p
    die(f"source not found: '{name}' (looked in Raw/{project}/, Reference/{project}/ and the repo root)")


def load(edit_path: Path) -> dict:
    edit = load_json(edit_path)
    edit["_path"] = edit_path
    project = edit.get("project") or edit_path.parent.name
    edit["project"] = project
    edit["_dir"] = EDITS / "Export" / project

    out = edit.setdefault("output", {})
    out.setdefault("width", 1080)
    out.setdefault("height", 1920)
    out.setdefault("fps", 30)
    out.setdefault("fit", "crop")
    if out["fit"] not in FITS:
        die(f"output.fit must be one of {sorted(FITS)}")
    if out["width"] % 2 or out["height"] % 2:
        die("output width and height must be even numbers")

    shots = edit.get("shots") or die("edit.json has no shots")
    cache: dict[Path, dict] = {}
    t = 0.0
    for i, s in enumerate(shots):
        s["_n"] = i + 1
        s["_src"] = _src(project, s.get("src") or die(f"shot {i + 1} has no src"))
        info = cache.setdefault(s["_src"], probe(s["_src"]))
        s["_info"] = info
        if "width" not in info:
            die(f"shot {i + 1}: {s['src']} has no video")
        s.setdefault("in", 0.0)
        s.setdefault("out", info["duration"])
        s.setdefault("speed", 1.0)
        if not 0 <= s["in"] < s["out"] <= info["duration"] + 0.05:
            die(f"shot {i + 1}: in/out ({s['in']}–{s['out']}) must be inside the clip (0–{info['duration']:.2f})")
        if not 0.25 <= s["speed"] <= 4:
            die(f"shot {i + 1}: speed must be between 0.25 and 4")
        s["_len"] = (s["out"] - s["in"]) / s["speed"]
        tr = s.get("transition") or {}
        if isinstance(tr, str):
            tr = {"type": tr}
        tr.setdefault("type", "cut")
        tr.setdefault("duration", 0.0 if tr["type"] == "cut" else 0.4)
        if tr["type"] == "cut":
            tr["duration"] = 0.0
        s["transition"] = tr
        if i > 0:
            d = shots[i - 1]["transition"]["duration"]
            if d >= min(shots[i - 1]["_len"], s["_len"]):
                die(f"transition after shot {i} ({d}s) is longer than shot {i} or {i + 1}")
            t -= d
        s["_start"] = t
        t += s["_len"]
    shots[-1]["transition"] = {"type": "cut", "duration": 0.0}
    edit["_total"] = t

    for x in edit.setdefault("texts", []):
        x.setdefault("position", "center")
        if x["position"] not in POSITIONS:
            die(f"text position must be one of {sorted(POSITIONS)}")
        x["end"] = min(x.get("end", t), t)
    return edit


def fit_filter(edit: dict, shot: dict, src_label: str, out_label: str, extra_scale: str = "") -> str:
    """Filter chain that frames one shot to the output size (crop / blur background / pad)."""
    o = edit["output"]
    W, H = o["width"], o["height"]
    fit = shot.get("fit", o["fit"])
    z = float(shot.get("zoom", 1.0))
    fx = float(shot.get("focus_x", 0.5))
    fy = float(shot.get("focus_y", 0.5))
    zw, zh = int(W * z) // 2 * 2, int(H * z) // 2 * 2
    if fit == "crop":
        chain = (f"{src_label}scale={zw}:{zh}:force_original_aspect_ratio=increase,"
                 f"crop={W}:{H}:(iw-{W})*{fx}:(ih-{H})*{fy}")
    elif fit == "pad":
        chain = (f"{src_label}scale={W}:{H}:force_original_aspect_ratio=decrease,"
                 f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:black")
    else:  # blur: blurred, filled copy behind the full frame
        k = out_label.strip("[]")
        chain = (f"{src_label}split[{k}bg][{k}fg];"
                 f"[{k}bg]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=25:2[{k}b];"
                 f"[{k}fg]scale={W}:{H}:force_original_aspect_ratio=decrease[{k}f];"
                 f"[{k}b][{k}f]overlay=(W-w)/2:(H-h)/2")
    return f"{chain},setsar=1{extra_scale}{out_label}"
