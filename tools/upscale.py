#!/usr/bin/env python3
"""AI 4x upscale (Real-ESRGAN x4plus, BSD-3) for product photos / cutouts, so posts stay sharp when zoomed.

    python3 tools/upscale.py "Video Edits/Raw/calsol-d/bottle-clean-cutout.png"      # -> ...-hd.png
    python3 tools/upscale.py in.png --out big.png --scale 2   (4x then Lanczos down to 2x)

Transparent PNGs: the colour is upscaled by the model, the alpha mask with Lanczos (clean edges).
The model (67 MB) downloads to assets/models/ on first use (git-ignored).
"""
import argparse
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image

R = Path(__file__).resolve().parent.parent
MODEL = R / "assets/models/RealESRGAN_x4plus.pth"
URL = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth"


def load():
    import torch
    from spandrel import ModelLoader
    if not MODEL.exists():
        MODEL.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(URL, MODEL)
    m = ModelLoader().load_from_file(str(MODEL)).model.eval()
    torch.set_num_threads(max(1, __import__("os").cpu_count() or 1))
    return m


def run(model, rgb: Image.Image, tile=256, pad=16) -> Image.Image:
    import torch
    x = torch.from_numpy(np.asarray(rgb).astype(np.float32) / 255).permute(2, 0, 1)[None]
    _, _, h, w = x.shape
    out = torch.zeros(1, 3, h * 4, w * 4)
    with torch.no_grad():
        for y0 in range(0, h, tile):
            for x0 in range(0, w, tile):
                ya, yb, xa, xb = max(0, y0 - pad), min(h, y0 + tile + pad), max(0, x0 - pad), min(w, x0 + tile + pad)
                o = model(x[:, :, ya:yb, xa:xb]).clamp(0, 1)
                oy, ox = (y0 - ya) * 4, (x0 - xa) * 4
                th, tw = min(tile, h - y0) * 4, min(tile, w - x0) * 4
                out[:, :, y0 * 4:y0 * 4 + th, x0 * 4:x0 * 4 + tw] = o[:, :, oy:oy + th, ox:ox + tw]
    return Image.fromarray((out[0].permute(1, 2, 0).numpy() * 255).round().astype("uint8"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src")
    ap.add_argument("--out")
    ap.add_argument("--scale", type=float, default=4)
    a = ap.parse_args()
    src = Path(a.src)
    im = Image.open(src)
    has_a = im.mode in ("RGBA", "LA") or "transparency" in im.info
    im = im.convert("RGBA")
    rgb = Image.new("RGB", im.size, (128, 128, 128)); rgb.paste(im, (0, 0), im)   # neutral fill under transparent px
    big = run(load(), rgb)
    if has_a:
        big.putalpha(im.split()[3].resize(big.size, Image.LANCZOS))
    if a.scale != 4:
        big = big.resize((round(im.width * a.scale), round(im.height * a.scale)), Image.LANCZOS)
    out = Path(a.out) if a.out else src.with_name(src.stem + "-hd.png")
    big.save(out)
    print(f"{out}  {im.size} -> {big.size}")


if __name__ == "__main__":
    main()
