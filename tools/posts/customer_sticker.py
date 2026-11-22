#!/usr/bin/env python3
"""Customer sticker / card (owner's reference: Video Edits/Reference/customer-sticker/ref.jpg).

Turns a customer's photo into a comic-style cut-out (smoothed colours + ink outlines), puts big bubbly text
above it (Luckiest Guy, white with a dark outline) on a warm textured background, plus a name pill.

    python3 tools/posts/customer_sticker.py --photo "<photo>" --name "Tariq Shirazi Sahab" \
        --line "TARIQ BHAI" --line "KA BHAROSA" [--urdu "طارق بھائی کا بھروسہ"] [--bg "#C8552E"] [--tag "KHYBER TRADERS"]

Writes  Video Edits/Export/customer-stickers/<slug>-card.jpg    (9:16, 2160x3840, for posts/status)
        Video Edits/Export/customer-stickers/<slug>-sticker.png (transparent sticker with white border, for video overlays)
"""
import argparse, json, re, subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as nd

R = Path(__file__).resolve().parents[2]
F = lambda g: str(next(R.joinpath('fonts').rglob(g)))


def comic(rgba: Image.Image) -> Image.Image:
    """Photo -> cartoon look: smoothed flat colours + dark ink lines, keeps alpha."""
    a = np.array(rgba).astype(np.float32)
    rgb, al = a[..., :3], a[..., 3]
    sm = rgb.copy()
    for _ in range(3):                                   # edge-aware-ish smoothing
        sm = nd.median_filter(sm, size=(7, 7, 1))
    sm = nd.gaussian_filter(sm, (1.2, 1.2, 0))
    q = np.round(sm / 22) * 22 + 8                       # gentle posterize (flat, painted colours)
    sm = q * 0.55 + sm * 0.45
    g = sm.mean(2)
    dog = nd.gaussian_filter(rgb.mean(2), 1.6) - nd.gaussian_filter(rgb.mean(2), 2.8)
    ink = np.clip((-dog - 3.0) / 6, 0, 1) * 0.8                # dark lines
    edge = (nd.gaussian_filter(al, 2) > 128) ^ nd.binary_erosion(nd.gaussian_filter(al, 2) > 128, iterations=3)
    ink = np.maximum(ink, edge * 1.0)
    sat = sm + (sm - g[..., None]) * 0.35                # a little more colour
    out = np.clip(sat * (1 - ink[..., None] * 0.85), 0, 255)
    o = np.dstack([out, al]).astype(np.uint8)
    return Image.fromarray(o)


def sticker(cut: Image.Image, border=18) -> Image.Image:
    a = np.array(cut); al = a[..., 3] > 100
    big = nd.binary_dilation(al, iterations=border)
    pad = Image.new("RGBA", cut.size, (0, 0, 0, 0))
    w = np.zeros(a.shape, np.uint8); w[big] = (255, 255, 255, 255)
    pad = Image.fromarray(w); pad.alpha_composite(cut)
    sh = pad.split()[3].filter(ImageFilter.GaussianBlur(10))
    out = Image.new("RGBA", (cut.width + 40, cut.height + 40), (0, 0, 0, 0))
    shadow = Image.new("RGBA", pad.size, (0, 0, 0, 120)); shadow.putalpha(sh.point(lambda v: v * 0.45))
    out.alpha_composite(shadow, (26, 30)); out.alpha_composite(pad, (20, 20))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--photo", required=True); ap.add_argument("--name", required=True)
    ap.add_argument("--line", action="append", default=[]); ap.add_argument("--urdu", default="")
    ap.add_argument("--bg", default="#C8552E"); ap.add_argument("--tag", default="")
    ap.add_argument("--crop", default="", help="x0,y0,x1,y1 fractions of the photo to keep (head + chest)")
    a = ap.parse_args()
    slug = re.sub(r"[^a-z0-9]+", "-", a.name.lower()).strip("-")
    d = R / "Video Edits/Export/customer-stickers"; w = d / "work"; w.mkdir(parents=True, exist_ok=True)
    src = Image.open(a.photo).convert("RGB")
    if a.crop:
        x0, y0, x1, y1 = [float(v) for v in a.crop.split(",")]
        src = src.crop((int(x0 * src.width), int(y0 * src.height), int(x1 * src.width), int(y1 * src.height)))
    sp = w / f"{slug}-src.jpg"; src.save(sp, quality=95)
    subprocess.run(["python3", str(R / "tools/cutout.py"), str(sp)], check=True, capture_output=True)
    cut = Image.open(w / f"{slug}-src-cutout.png").convert("RGBA")
    if cut.width < 1100:
        k = 1100 / cut.width; cut = cut.resize((int(cut.width * k), int(cut.height * k)), Image.LANCZOS)
    toon = comic(cut); tp = w / f"{slug}-toon.png"; toon.save(tp)
    st = sticker(toon); st.save(d / f"{slug}-sticker.png")
    fonts = [{"family": "Luckiest", "path": F("LuckiestGuy-400.ttf"), "weight": 400, "style": "normal"},
             {"family": "Lalezar", "path": F("Lalezar-400.ttf"), "weight": 400, "style": "normal"},
             {"family": "Poppins", "path": F("Poppins-800.ttf"), "weight": 800, "style": "normal"},
             {"family": "Poppins", "path": F("Poppins-600.ttf"), "weight": 600, "style": "normal"}]
    lines = "".join(f'<div class="t" style="font-size:{170 if len(l) < 9 else 132}px">{l}</div>' for l in a.line)
    urdu = f'<div class="u">{a.urdu}</div>' if a.urdu else ""
    tag = f'<div class="tag">{a.tag}</div>' if a.tag else ""
    css = f"""*{{margin:0;padding:0;box-sizing:border-box}}
#p{{position:absolute;inset:0;overflow:hidden;background:{a.bg}}}
.tex{{position:absolute;inset:0;background:url(file://{w}/tex.png);background-size:540px 960px;mix-blend-mode:overlay;opacity:.9}}
.vig{{position:absolute;inset:0;background:radial-gradient(ellipse 80% 60% at 50% 45%,transparent 40%,rgba(0,0,0,.35))}}
.hd{{position:absolute;top:170px;left:40px;right:40px;text-align:center;font-family:Luckiest;color:#fff;line-height:.95;text-transform:uppercase}}
.t{{-webkit-text-stroke:14px #2a1208;paint-order:stroke fill;text-shadow:0 12px 0 #2a1208,0 20px 30px rgba(0,0,0,.35);letter-spacing:1px}}
.u{{font:118px/1.4 Lalezar;direction:rtl;color:#FFD84A;-webkit-text-stroke:12px #2a1208;paint-order:stroke fill;text-shadow:0 10px 0 #2a1208;margin-top:6px}}
.ph{{position:absolute;left:50%;bottom:-40px;transform:translateX(-50%);width:1240px;filter:drop-shadow(0 30px 40px rgba(0,0,0,.4))}}
.nm{{position:absolute;bottom:140px;left:50%;transform:translateX(-50%);white-space:nowrap;background:#fff;border-radius:60px;padding:16px 44px 14px;
 font:800 46px Poppins;color:#2a1208;border:6px solid #2a1208;box-shadow:0 10px 0 #2a1208}}
.tag{{position:absolute;bottom:250px;right:130px;transform:rotate(-4deg);background:#FFD84A;border:5px solid #2a1208;border-radius:12px;padding:8px 18px 6px;
 font:800 26px Poppins;color:#2a1208;letter-spacing:1px}}"""
    rng = np.random.default_rng(3); n = rng.normal(128, 70, (960, 540)); n = nd.gaussian_filter(n, 0.6)
    Image.fromarray(np.clip(n, 0, 255).astype(np.uint8)).resize((1080, 1920)).save(w / "tex.png")
    html = f'<div id="p"><div class="tex"></div><div class="vig"></div><img class="ph" src="file://{tp}"><div class="hd">{lines}{urdu}</div>{tag}<div class="nm">{a.name}</div></div>'
    out = d / f"{slug}-card.png"; job = d / "job.json"
    job.write_text(json.dumps({"width": 1080, "height": 1920, "scale": 2, "css": css, "fonts": fonts, "states": [{"file": str(out), "html": html}]}))
    subprocess.run(["node", str(R / "tools/htmlcaps/render.js"), str(job)], check=True, capture_output=True)
    job.unlink(); (d / "page.html").unlink(missing_ok=True)
    Image.open(out).convert("RGB").save(d / f"{slug}-card.jpg", quality=95); out.unlink()
    print(d / f"{slug}-card.jpg"); print(d / f"{slug}-sticker.png")


if __name__ == "__main__":
    main()
