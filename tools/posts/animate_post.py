#!/usr/bin/env python3
"""Animate a 3:4 product post (from to_3x4.py) with a voice-over: elements enter on the spoken words.

    python3 tools/posts/animate_post.py tools/posts/anim/heavy-gold.json

anim json: {"post": "heavy-gold.json", "name": "heavy-gold-anim", "voice": "ur-PK-AsadNeural", "rate": "+12%",
            "lines": [["text", start_s], ...], "enter": {".hero": 2.35, ...}, "sfx": [["whoosh", t, vol], ...], "end": 21}
"""
import json, re, runpy, subprocess, sys, os
from pathlib import Path
R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R / "tools")); sys.path.insert(0, str(R / "tools/posts"))
import to_3x4
from sfx import get as sfx_get

ANIM_CSS = """
@keyframes rise{from{opacity:0;translate:0 60px;scale:.96}to{opacity:1;translate:0 0;scale:1}}
@keyframes slam{0%{opacity:0;scale:1.6}60%{opacity:1;scale:.96}100%{opacity:1;scale:1}}
@keyframes pop{0%{opacity:0;scale:.3}70%{opacity:1;scale:1.08}100%{opacity:1;scale:1}}
@keyframes bagin{from{opacity:0;translate:0 140px;scale:.85}to{opacity:1;translate:0 0;scale:1}}
@keyframes float{from{translate:0 0}to{translate:0 -14px}}
@keyframes upbar{from{opacity:0;translate:0 200px}to{opacity:1;translate:0 0}}
@keyframes pulse{0%,100%{scale:1}50%{scale:1.07}}
@keyframes push{from{scale:1}to{scale:1.05}}
"""
KIND = {".top": "rise .5s", ".l1": "rise .6s", ".hero": "slam .55s", ".tonic": "slam .55s", ".bag": "bagin .8s",
        ".c1": "pop .5s", ".c2": "pop .5s", ".l4": "rise .5s", ".l5": "rise .5s", ".ft": "rise .5s", "#kt3": "upbar .6s"}


def main():
    argv = list(sys.argv); a = json.loads(Path(argv[1]).read_text())
    name, end, fps = a["name"], a["end"], a.get("fps", 30)
    d = R / "Video Edits/Export" / name; w = d / "work"; w.mkdir(parents=True, exist_ok=True)
    # 1. capture the 3:4 job of the post
    cap = {}
    real = subprocess.run
    def fake(cmd, *x, **k):
        if isinstance(cmd, list) and cmd[:1] == ["node"] and cmd[1].endswith("render.js"):
            job = json.loads(Path(cmd[2]).read_text()); cap["job"] = to_3x4.transform(job, "x")
        return real(cmd, *x, **k)
    subprocess.run = fake
    sys.argv = ["product_post.py", str(R / "tools/posts" / a["post"])]
    runpy.run_path(str(R / "tools/posts/product_post.py"), run_name="__main__")
    subprocess.run = real
    job = cap["job"]
    # 2. animations
    css = ANIM_CSS
    for sel, t in a["enter"].items():
        extra = ""
        if sel == ".bag":
            extra = f",float 3s ease-in-out {t + .8}s infinite alternate"
        if sel == "#kt3":
            extra = f",pulse .9s ease-in-out {t + .8}s 3"
        css += f"#cap {sel}{{animation:{KIND.get(sel, 'rise .5s')} cubic-bezier(.2,.8,.2,1) {t}s both{extra}}}\n"
    css += f"#wrap{{animation:push {end}s linear 0s both}} #wrap{{transform-origin:50% 45%}}\n"
    job["css"] += css
    jp = w / "anim-job.json"; jp.write_text(json.dumps(job))
    frames = w / "frames"
    if "--audio-only" not in argv:
      subprocess.run(["rm", "-rf", str(frames)])
      subprocess.run(["node", str(R / "tools/posts/anim_frames.js"), str(jp), str(frames), str(fps), str(end), str(a.get("scale", 1.5))], check=True)
    # 3. voice
    env = dict(os.environ, SSL_CERT_FILE="/root/.ccr/ca-bundle.crt")
    ins, filt = [], []
    for i, (text, t) in enumerate(a["lines"]):
        mp = w / f"v{i}.mp3"
        cmd = ["edge-tts", "--voice", a.get("voice", "ur-PK-AsadNeural"), f"--rate={a.get('rate', '+12%')}", f"--pitch={a.get('pitch', '+4Hz')}", "--text", text, "--write-media", str(mp)]
        if os.environ.get("HTTPS_PROXY"): cmd[1:1] = ["--proxy", os.environ["HTTPS_PROXY"]]
        subprocess.run(cmd, check=True, capture_output=True, env=env)
        ins += ["-i", str(mp)]; n = len(ins) // 2
        filt.append(f"[{n}:a]adelay={int(t*1000)}|{int(t*1000)},volume={a.get('voice_vol', 1.0)}[a{n}]")
    for s, t, v in a.get("sfx", []):
        ins += ["-i", str(sfx_get(s, a.get("sfx_bank", "")))]; n = len(ins) // 2
        filt.append(f"[{n}:a]adelay={int(t*1000)}|{int(t*1000)},volume={v}[a{n}]")
    k = len(ins) // 2
    filt.append("".join(f"[a{i}]" for i in range(1, k + 1)) + f"amix=inputs={k}:normalize=0,atrim=0:{end},loudnorm=I=-14:TP=-1.5[out]")
    out = d / f"{name}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(fps), "-i", str(frames / "f%05d.jpg"), *ins,
                    "-filter_complex", ";".join(filt), "-map", "0:v", "-map", "[out]", "-c:v", "libx264", "-preset", "slow",
                    "-crf", "17", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", str(out)], check=True)
    print(out)


if __name__ == "__main__":
    main()
