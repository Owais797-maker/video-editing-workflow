#!/usr/bin/env python3
"""Re-render the 9:16 product posts as 3:4 (2880x3840, 4K) with the Khyber Traders bar at the bottom.

    python3 tools/posts/to_3x4.py                 # every post in the series
    python3 tools/posts/to_3x4.py heavy-gold.json tolomec_post.py

Each post script runs unchanged; its render job is intercepted: the 1080x1920 layout is scaled into a
1440x1920 canvas (same background, wider), any KT pill/bar inside the post is removed, and one KT bar
(official wordmark + WhatsApp number) goes along the bottom. Output: Video Edits/Export/posts-3x4/<name>.jpg
"""
import json
import os
import re
import runpy
import subprocess
import sys
from pathlib import Path

R = Path(__file__).resolve().parents[2]
OUT = R / "Video Edits/Export/posts-3x4"
NUMBER = "0310-2999262"
JSONS = ["heavy-gold", "heavy-gold-pouch", "buttery-milk", "mega-vmix", "power-vimix", "mega-tox", "mega-tox-clay", "hepta-sef",
         "gripe-water", "milkolin", "ratawa", "lacto-sol", "novasil", "novasil-colour", "ear-tags"]
SCRIPTS = ["megatox_detail.py", "antox9_post.py", "tolomec_post.py", "aftodoll_post.py", "ivermectin_post.py"]
W, H, BAR = 1440, 1920, 150           # css px; scale 2 -> 2880x3840
WA = ('<svg width="34" height="34" viewBox="0 0 24 24"><path fill="#1B1B1F" d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm5.3 14.1c-.2.6-1.3 1.2-1.8 1.2-.5.1-1 .1-3.3-.8-2.8-1.1-4.5-4-4.7-4.2-.1-.2-1.1-1.5-1.1-2.9s.7-2 1-2.3c.2-.3.5-.3.7-.3h.5c.2 0 .4 0 .6.5l.8 2c.1.2.1.3 0 .5l-.4.5-.3.4c-.1.1-.3.3-.1.6.2.3.8 1.3 1.7 2.1 1.2 1 2.1 1.3 2.4 1.5.3.1.5.1.6-.1l.9-1c.2-.3.4-.2.6-.1l1.9.9c.3.1.5.2.5.3.1.2.1.7-.1 1.2z"/></svg>')
KT_CSS = f"""
#wrap{{position:absolute;left:{(W - 1080 * (H - BAR) / 1920) / 2}px;top:0;width:1080px;height:1920px;transform:scale({(H - BAR) / 1920});transform-origin:0 0}}
#wrap #p{{background:none!important}} #wrap .sheen,#wrap .kt{{display:none!important}}
#kt3{{position:absolute;left:60px;right:60px;bottom:34px;height:124px;border-radius:64px;background:#1B1B1F;display:flex;align-items:center;padding:0 26px 0 40px;box-shadow:0 14px 30px rgba(0,0,0,.18);z-index:9}}
#kt3 img{{height:80px}} #kt3 .ph{{margin-left:auto;display:flex;align-items:center;gap:12px;background:#FFD400;color:#1B1B1F;border-radius:44px;padding:16px 30px;font:900 38px Montserrat;letter-spacing:.5px}}
"""


def transform(job: dict, name: str) -> dict:
    st = job["states"][0]
    html = st["html"]
    html = re.sub(r'<bdi[^>]*>KHYBER TRADERS.*?</bdi>', '', html, flags=re.S)   # old KT pill (ratawa, lacto-sol-kt)
    bar = (f'<div id="kt3"><img src="file://{R}/assets/logos/khyber-traders-wordmark-white-red.png">'
           f'<div class="ph">{WA}{NUMBER}</div></div>')
    if os.environ.get("NO_KT"):      # reseller version: no shop name / number, layout keeps its full size
        bar = ""
        job["css"] += "#wrap{transform:scale(1)!important;left:180px!important}"
    st["html"] = f'<div id="p"><div class="sheen"></div></div><div id="wrap">{html}</div>{bar}'
    st["file"] = str(OUT / f"{name}.jpg")
    job["width"], job["height"], job["scale"] = W, H, 2
    job["css"] += KT_CSS
    return job


def run(target: str) -> None:
    real = subprocess.run

    def fake(cmd, *a, **k):
        if isinstance(cmd, list) and cmd[:1] == ["node"] and cmd[1].endswith("render.js"):
            jp = Path(cmd[2])
            job = json.loads(jp.read_text())
            out = Path(job["states"][0]["file"])
            new = jp.with_name("job-3x4.json")
            png = OUT / f"{out.stem}.png"
            job = transform(job, out.stem)
            job["states"][0]["file"] = str(png)
            new.write_text(json.dumps(job))
            real(["node", cmd[1], str(new)], check=True, capture_output=True)
            new.unlink()
            from PIL import Image
            Image.open(png).convert("RGB").save(OUT / f"{out.stem}.jpg", quality=95)
            png.unlink()
            print("->", (OUT / f"{out.stem}.jpg").relative_to(R))
            return real(cmd, *a, **k)  # the normal 9:16 render too, so the post script finishes as usual
        return real(cmd, *a, **k)

    subprocess.run = fake
    try:
        if target.endswith(".json"):
            sys.argv = ["product_post.py", str(R / "tools/posts" / target)]
            runpy.run_path(str(R / "tools/posts/product_post.py"), run_name="__main__")
        else:
            sys.argv = [target]
            runpy.run_path(str(R / "tools/posts" / target), run_name="__main__")
    finally:
        subprocess.run = real


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    targets = sys.argv[1:] or [j + ".json" for j in JSONS] + SCRIPTS
    for t in targets:
        run(t)


if __name__ == "__main__":
    main()
