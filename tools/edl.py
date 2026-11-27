"""Load and validate an edit.json (the edit decision list) and work out its timeline.

Shared by captions.py, storyboard.py and render.py, so the storyboard always
shows exactly what render.py will produce. The format is documented in
tools/EDIT_FORMAT.md.
"""
from __future__ import annotations

from pathlib import Path

from common import EDITS, REPO, die, load_json, probe

STYLES = REPO / "styles"
FITS = {"crop", "blur", "pad"}
POSITIONS = {"top": 8, "center": 5, "bottom": 2}
MOTIONS = {"none", "zoom_in", "zoom_out", "pan_left", "pan_right", "pan_up", "pan_down"}
TEXT_ANIMS = {"none", "fade", "pop", "slide_up", "slide_left", "typewriter"}


def _merge(base: dict, over: dict) -> dict:
    """Deep merge: values in `over` win."""
    out = dict(base)
    for k, v in over.items():
        out[k] = _merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def default_style() -> str | None:
    f = STYLES / "default.txt"
    if not f.exists():
        return None
    return f.read_text(encoding="utf-8").strip() or None


def apply_style(edit: dict) -> None:
    """Fill in everything the edit doesn't set from styles/<name>/style.json."""
    name = edit.get("style", default_style())
    if not name:
        return
    f = STYLES / name / "style.json"
    if not f.exists():
        die(f"style '{name}' not found ({f.relative_to(REPO)})")
    st = load_json(f)
    edit["_style"] = name
    for key in ("output", "look", "fade"):
        if key in st:
            edit[key] = _merge(st[key], edit.get(key) or {})
    if "type_presets" in st:
        edit["type_presets"] = _merge(st["type_presets"], edit.get("type_presets") or {})
    for key in ("loudness", "progress_bar", "quality", "safe", "brand", "sfx_bank"):
        if key in st and key not in edit:
            edit[key] = st[key]
    if edit.get("captions") is not None and edit.get("captions") is not False and "captions" in st:
        cap = edit["captions"] if isinstance(edit["captions"], dict) else {}
        edit["captions"] = _merge(st["captions"], cap)
    if edit.get("music") and "music" in st:
        edit["music"] = _merge(st["music"], edit["music"])
    shots = edit.get("shots") or []
    for i, sh in enumerate(shots):
        if "transition" in st and "transition" not in sh and i < len(shots) - 1:
            sh["transition"] = st["transition"]
        if "motion" in st and "motion" not in sh:
            sh["motion"] = st["motion"]
    for x in edit.get("texts", []):
        kind = x.get("type", "title")
        defaults = st.get("lower_third" if kind == "lower_third" else "text", {})
        for k, v in defaults.items():
            x.setdefault(k, v)
    for o in edit.get("overlays", []):
        for k, v in st.get("overlay", {}).items():
            o.setdefault(k, v)
    # glass: widgets (label/value) and plain discs/boxes get the locked house look
    for gl in edit.get("glass", []):
        if gl.get("crystal"):  # clear lens: keep its own look (the frosted house defaults would blur it)
            continue
        kind = ("widget_dark" if gl.get("theme") == "dark" else "widget") if gl.get("value") else "plain"
        for k, v in (st.get("glass", {}).get(kind) or {}).items():
            gl.setdefault(k, v)


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
    if edit.get("captions") is True:
        edit["captions"] = {}
    apply_style(edit)
    if not edit.get("captions"):
        edit["captions"] = None

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
        m = s.get("motion") or {}
        if isinstance(m, str):
            m = {"type": m}
        m.setdefault("type", "none")
        if m["type"] not in MOTIONS:
            die(f"shot {i + 1}: motion must be one of {sorted(MOTIONS)}")
        m.setdefault("amount", 0.12)
        s["motion"] = m
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
        if x.get("segments") and "text" not in x:
            x["text"] = " ".join(sg["text"] for sg in x["segments"])
        x.setdefault("position", "center")
        if x["position"] not in POSITIONS:
            die(f"text position must be one of {sorted(POSITIONS)}")
        if x.get("animation", "fade") not in TEXT_ANIMS:
            die(f"text animation must be one of {sorted(TEXT_ANIMS)}")
        x["end"] = min(x.get("end", t), t)
    safe = edit.get("safe") or {}
    if safe:
        lo, hi = float(safe.get("top", 0)) + 0.03, 1 - float(safe.get("bottom", 0)) - 0.03
        for x in edit["texts"]:
            if "y" in x and x.get("type") != "lower_third":
                x["y"] = min(max(float(x["y"]), lo), hi)
        for g in edit.get("glass", []):
            g["y"] = min(max(float(g.get("y", 0.5)), lo), hi)
    for o in edit.setdefault("overlays", []):
        if not (o.get("file") or o.get("emoji")):
            die("each overlay needs \"file\" or \"emoji\"")
        o.setdefault("start", 0)
        o["end"] = min(o.get("end", t), t)
    return edit


def motion_filter(edit: dict, shot: dict) -> str:
    """Per-frame zoom / pan / punch-in / shake on an already framed shot.

    Runs after fps=..., so time = in/fps. Uses the perspective filter (sub-pixel,
    no frame-size changes), which gives smooth movement."""
    W, H, fps = edit["output"]["width"], edit["output"]["height"], edit["output"]["fps"]
    m, L = shot["motion"], shot["_len"]
    a = float(m["amount"])
    punches = shot.get("punch") or []
    shakes = shot.get("shake") or []
    if m["type"] == "none" and not punches and not shakes:
        return ""
    t = f"(in/{fps})"
    p = f"min({t}/{L:.3f},1)"
    z = {"zoom_in": f"1+{a}*{p}", "zoom_out": f"1+{a}*(1-{p})"}.get(m["type"], f"1+{a}" if m["type"] != "none" else "1")
    if shakes and m["type"] == "none":
        z = "1.06"
    pz = float(shot.get("punch_zoom", 1.15)) - 1
    for s0, s1 in punches:
        z += f"+{pz}*between({t},{s0},{s1})"
    z = f"({z})"
    hw, hh = f"({W}/2/{z})", f"({H}/2/{z})"
    cx = {"pan_left": f"{hw}+({W}-2*{hw})*{p}", "pan_right": f"{W}-{hw}-({W}-2*{hw})*{p}"}.get(m["type"], f"{W}/2")
    cy = {"pan_up": f"{hh}+({H}-2*{hh})*{p}", "pan_down": f"{H}-{hh}-({H}-2*{hh})*{p}"}.get(m["type"], f"{H}/2")
    amt = float(shot.get("shake_amount", 14))
    for s0, s1 in shakes:
        cx += f"+{amt}*sin({t}*47)*between({t},{s0},{s1})"
        cy += f"+{amt}*cos({t}*39)*between({t},{s0},{s1})"
    cx, cy = f"clip({cx},{hw},{W}-{hw})", f"clip({cy},{hh},{H}-{hh})"
    x0, x1 = f"{cx}-{hw}", f"{cx}+{hw}"
    y0, y1 = f"{cy}-{hh}", f"{cy}+{hh}"
    return (f",perspective=x0='{x0}':y0='{y0}':x1='{x1}':y1='{y0}':x2='{x0}':y2='{y1}':x3='{x1}':y3='{y1}'"
            f":interpolation=cubic:sense=source:eval=frame")


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
        chain = (f"{src_label}scale={zw}:{zh}:force_original_aspect_ratio=increase:flags=lanczos,"
                 f"crop={W}:{H}:(iw-{W})*{fx}:(ih-{H})*{fy}")
    elif fit == "pad":
        chain = (f"{src_label}scale={W}:{H}:force_original_aspect_ratio=decrease:flags=lanczos,"
                 f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:black")
    else:  # blur: blurred, filled copy behind the full frame
        k = out_label.strip("[]")
        chain = (f"{src_label}split[{k}bg][{k}fg];"
                 f"[{k}bg]scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},boxblur=25:2[{k}b];"
                 f"[{k}fg]scale={W}:{H}:force_original_aspect_ratio=decrease:flags=lanczos[{k}f];"
                 f"[{k}b][{k}f]overlay=(W-w)/2:(H-h)/2")
    return f"{chain},setsar=1{extra_scale}{out_label}"
