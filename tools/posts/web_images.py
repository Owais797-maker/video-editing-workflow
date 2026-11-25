#!/usr/bin/env python3
"""Website product images: square 1600x1600 JPG, pure white, product centred at ~84% of the frame, soft ground
shadow, no text/badges (Google Merchant Center safe). Also one PDF with all of them + a zip of the JPGs.

    python3 tools/posts/web_images.py
"""
import subprocess, sys, zipfile
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
R = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(R / "tools/posts"))
from ground import ground
RAW = R / "Video Edits/Raw"; OUT = R / "Video Edits/Export/website-images"; W = OUT / "work"
SIZE, FILL = 1600, 0.84
# (file name, source, grounded already?, auto-levels box photo?)
P = [("heavy-gold-20kg", "heavy-gold/heavy-gold-bag-cutout.png", 0, 0), ("heavy-gold-1kg-pouch", "heavy-gold-pouch/pouch-cutout.png", 0, 0),
     ("buttery-milk-20kg", "butter-milk/butter-milk-bag-cutout.png", 0, 0), ("mega-vmix-25kg", "mega-vmix/mega-vmix-bag-cutout.png", 0, 0),
     ("power-vimix-5kg", "power-vimix/power-vimix-reseller-cutout.png", 0, 0), ("lacto-sol-1kg", "lacto-sol/lacto-sol-pouch-cutout.png", 0, 0),
     ("hepta-sef-5l", "three-products/hepta-sef-cutout.png", 0, 0), ("life-gripe-water-5l", "bacha-hairan/gripe-water-mockup-cutout.png", 0, 0),
     ("milkolin-plus-1l", "milkolin/milkolin-clean-cutout.png", 0, 0), ("ratawa-spray-200ml", "ratawa/ratawa-cutout.png", 0, 0),
     ("mega-tox-plus-25kg", "mega-tox/mega-tox-bag-cutout.png", 0, 0), ("mega-tox-clay-25kg", "mega-tox-clay/bag-crop-cutout.png", 0, 0),
     ("basf-novasil-plus-25kg", "novasil/novasil-cutout.png", 0, 0), ("printed-ear-tags", "ear-tags/tags-composite.png", 0, 0),
     ("antox-9-vaccine", "antox9/box-crop-cutout.png", 0, 1), ("tolomec-plus-500ml", "tolomec/box-grounded.png", 1, 1),
     ("aftodoll-jel-vaccine", "aftodoll/box-grounded.png", 1, 1)]


def levels(im):
    a = im.split()[3]; m = np.asarray(a) > 128
    x = np.asarray(im.convert("RGB")).astype(np.float32) / 255
    lo = np.percentile(x[m], 1.5, axis=0); hi = np.percentile(x[m], 98.5, axis=0)
    x = np.clip((np.clip((x - lo) / (hi - lo), 0, 1) ** 0.95 - .5) * 1.04 + .5, 0, 1)
    out = Image.fromarray((x * 255).astype("uint8")); out.putalpha(a); return out


def make(name, src, grounded, lv):
    im = Image.open(RAW / src).convert("RGBA")
    if lv: im = levels(im)
    a = np.asarray(im.split()[3])
    obj = Image.fromarray(((a > 200) * 255).astype("uint8")).getbbox()       # the product itself (not its soft shadow)
    if not grounded:
        tmp = W / f"{name}-g.png"; im.save(W / f"{name}-src.png"); ground(str(W / f"{name}-src.png"), str(tmp)); g = Image.open(tmp).convert("RGBA")
        pad_x = (g.width - im.width) // 2; obj = (obj[0] + pad_x, obj[1], obj[2] + pad_x, obj[3])   # ground pads sides equally, top 0
        if g.size[1] - im.size[1] > 0: pass
        im = g
    ow, oh = obj[2] - obj[0], obj[3] - obj[1]
    s = SIZE * FILL / max(ow, oh)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    if s > 1: im = im.filter(ImageFilter.UnsharpMask(1.6, 60, 2))
    cx, cy = (obj[0] + obj[2]) / 2 * s, (obj[1] + obj[3]) / 2 * s
    can = Image.new("RGB", (SIZE, SIZE), "white")
    can.paste(im, (round(SIZE / 2 - cx), round(SIZE / 2 - cy)), im)
    f = OUT / f"{name}.jpg"; can.save(f, quality=95, subsampling=0); return f


def main():
    W.mkdir(parents=True, exist_ok=True)
    fs = [make(*p) for p in P]
    for f in fs: print(f.name)
    imgs = [Image.open(f).convert("RGB") for f in fs]
    imgs[0].save(OUT / "khyber-traders-website-images.pdf", save_all=True, append_images=imgs[1:], resolution=200, quality=95)
    with zipfile.ZipFile(OUT / "Khyber-Website-Images.zip", "w", zipfile.ZIP_STORED) as z:
        for f in fs: z.write(f, f"Khyber-Website-Images/{f.name}")
        z.write(OUT / "khyber-traders-website-images.pdf", "Khyber-Website-Images/khyber-traders-website-images.pdf")


if __name__ == "__main__":
    main()
