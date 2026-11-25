#!/usr/bin/env python3
"""Make a product cutout sit on the ground: adds a contact shadow that follows the real bottom edges
(perspective-aware, per column) + a soft ambient shadow. Output = RGBA with the shadow baked in.
    python3 tools/posts/ground.py <cutout.png> <out.png> [--light left|right]"""
import sys
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as nd

def ground(src, out, light="left"):
    im = Image.open(src).convert("RGBA"); im = im.crop(im.getbbox())
    a = np.array(im)[..., 3] > 100
    H, W = a.shape; pad = int(H * 0.12); side = int(W * 0.12)
    sh = np.zeros((H + pad, W + 2 * side), np.float32)
    base = np.full(W, -1)
    for x in range(W):
        c = np.where(a[:, x])[0]
        if len(c): base[x] = c.max()
    xs = np.where(base >= 0)[0]
    for x in xs:                                   # contact shadow: dark right at the edge, fading down
        y0 = base[x]; L = int(H * 0.035)
        for k in range(L):
            sh[y0 - 2 + k, x + side] = max(sh[y0 - 2 + k, x + side], (1 - k / L) ** 1.6)
    contact = nd.gaussian_filter(sh, (3, 2.5)) * 0.95
    amb = np.zeros_like(sh)                         # ambient: footprint smeared away from the light
    for x in xs:
        y0 = base[x]; L = int(H * 0.09)
        for k in range(L):
            amb[y0 - 4 + k, x + side] = max(amb[y0 - 4 + k, x + side], (1 - k / L) ** 1.2)
    shift = int(W * 0.05) * (1 if light == "left" else -1)
    amb = nd.shift(amb, (0, shift), order=1)
    amb = nd.gaussian_filter(amb, (int(H * 0.012) + 4, int(W * 0.03) + 6)) * 0.55
    alpha = np.clip(np.maximum(contact, amb), 0, 1)
    canvas = Image.new("RGBA", (W + 2 * side, H + pad), (0, 0, 0, 0))
    shadow = Image.fromarray((alpha * 255).astype(np.uint8))
    canvas.paste(Image.new("RGBA", canvas.size, (20, 18, 28, 255)), (0, 0), shadow)
    canvas.alpha_composite(im, (side, 0))
    canvas.save(out)

if __name__ == "__main__":
    ground(sys.argv[1], sys.argv[2], sys.argv[4] if len(sys.argv) > 4 else "left")
