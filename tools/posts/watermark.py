#!/usr/bin/env python3
"""Khyber Traders watermark on the website images (separate copies; the clean ones stay for Google Merchant).
A faint diagonal KT wordmark across the product (hard to crop out) + a small logo in the corner.

    python3 tools/posts/watermark.py
"""
import zipfile
from pathlib import Path
from PIL import Image, ImageEnhance
R = Path(__file__).resolve().parents[2]
SRC = R / "Video Edits/Export/website-images"; OUT = SRC / "watermarked"
LOGO = Image.open(R / "assets/logos/khyber-traders-wordmark.png").convert("RGBA")


def faded(im, op):
    a = im.split()[3].point(lambda v: int(v * op)); im = im.copy(); im.putalpha(a); return im


def mark(f):
    im = Image.open(f).convert("RGBA"); S = im.width
    big = LOGO.resize((int(S * .78), int(LOGO.height * S * .78 / LOGO.width)), Image.LANCZOS)
    big = faded(big, .13).rotate(28, expand=True, resample=Image.BICUBIC)
    im.alpha_composite(big, ((S - big.width) // 2, (S - big.height) // 2 + int(S * .04)))
    sm = LOGO.resize((int(S * .26), int(LOGO.height * S * .26 / LOGO.width)), Image.LANCZOS)
    im.alpha_composite(faded(sm, .85), (S - sm.width - int(S * .035), S - sm.height - int(S * .03)))
    out = OUT / f.name; im.convert("RGB").save(out, quality=95, subsampling=0); return out


def main():
    OUT.mkdir(exist_ok=True)
    fs = [mark(f) for f in sorted(SRC.glob("*.jpg"))]
    imgs = [Image.open(f) for f in fs]
    pdf = OUT / "khyber-traders-images-watermark.pdf"
    imgs[0].save(pdf, save_all=True, append_images=imgs[1:], resolution=200, quality=95)
    with zipfile.ZipFile(SRC / "Khyber-Images-Watermark.zip", "w", zipfile.ZIP_STORED) as z:
        for f in fs + [pdf]: z.write(f, f"Khyber-Images-Watermark/{f.name}")
    print(len(fs))


if __name__ == "__main__":
    main()
