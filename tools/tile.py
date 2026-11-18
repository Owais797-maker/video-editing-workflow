#!/usr/bin/env python3
"""Glossy app-icon style tile (rounded square, colour gradient, top shine, emoji in the middle),
like the blue icon tiles that pop in a row in motion-graphics reels.

    python tools/tile.py --project my-reel --name vitamins --emoji 💊 --color "#1E4FA8"

Writes Video Edits/Raw/<project>/tile-<name>.png (transparent, 600x600). Use as an overlay
(width ~0.13, animation pop) and line several up in a row as the features are spoken.
"""
import argparse

from badge import emoji_png
from common import EDITS


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--emoji", required=True)
    ap.add_argument("--color", default="#1E4FA8")
    args = ap.parse_args()
    from PIL import Image, ImageDraw, ImageFilter

    S, ss = 600, 2
    N = S * ss
    pad, rad = int(N * 0.08), int(N * 0.24)
    base = hexrgb(args.color)
    light = tuple(min(255, int(c + (255 - c) * 0.45)) for c in base)
    dark = tuple(int(c * 0.62) for c in base)
    # vertical gradient light -> base -> dark
    grad = Image.new("RGBA", (N, N))
    gd = ImageDraw.Draw(grad)
    for y in range(N):
        t = y / N
        a, b, u = (light, base, t / 0.5) if t < 0.5 else (base, dark, (t - 0.5) / 0.5)
        gd.line([(0, y), (N, y)], fill=tuple(int(a[i] + (b[i] - a[i]) * u) for i in range(3)) + (255,))
    mask = Image.new("L", (N, N), 0)
    ImageDraw.Draw(mask).rounded_rectangle([pad, pad, N - pad, N - pad], rad, fill=255)
    out = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    # soft drop shadow
    sh = Image.new("L", (N, N), 0)
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + int(N * 0.03), N - pad, N - pad + int(N * 0.03)], rad, fill=120)
    sh = sh.filter(ImageFilter.GaussianBlur(N * 0.025))
    out.paste(Image.new("RGBA", (N, N), (0, 0, 0, 255)), (0, 0), sh)
    out.paste(grad, (0, 0), mask)
    # glossy shine on the top half
    shine = Image.new("L", (N, N), 0)
    ImageDraw.Draw(shine).rounded_rectangle([pad + 8, pad + 8, N - pad - 8, int(N * 0.5)], rad - 8, fill=70)
    shine = shine.filter(ImageFilter.GaussianBlur(N * 0.02))
    shine = Image.composite(shine, Image.new("L", (N, N), 0), mask)
    out.paste(Image.new("RGBA", (N, N), (255, 255, 255, 255)), (0, 0), shine)
    # thin light rim
    rim = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    ImageDraw.Draw(rim).rounded_rectangle([pad, pad, N - pad, N - pad], rad, outline=(255, 255, 255, 150), width=int(N * 0.008))
    out = Image.alpha_composite(out, rim)
    # emoji
    em = emoji_png(args.emoji)
    es = int(N * 0.5)
    em = em.resize((es, es), Image.LANCZOS)
    out.alpha_composite(em, ((N - es) // 2, (N - es) // 2))
    out = out.resize((S, S), Image.LANCZOS)
    dest = EDITS / "Raw" / args.project / f"tile-{args.name}.png"
    dest.parent.mkdir(parents=True, exist_ok=True)
    out.save(dest)
    print(f"Tile: {dest}")


if __name__ == "__main__":
    main()
