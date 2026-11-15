#!/usr/bin/env python3
"""Make a round icon badge (sticker) for overlays: coloured ring, emoji icon, bold label.

    python tools/badge.py --project heavy-gold --label VITAMINS --emoji 💊 --color "#8E44AD"
        -> Video Edits/Raw/heavy-gold/badge-vitamins.png

Options: --sub "JAPAN"  small second line;  --corner-emoji 🇯🇵  small emoji on the ring;
--font "Anton" (any font file name stem in fonts/, default Poppins ExtraBold).
"""
import argparse
import re
import urllib.request

from common import EDITS, REPO, die, font_files

S = 600  # canvas size (px); scaled down in the video


def emoji_png(emoji: str):
    from PIL import Image
    cps = "_".join(f"{ord(ch):x}" for ch in emoji if ord(ch) != 0xFE0F)
    dest = REPO / "assets" / "emoji" / f"{cps}.png"
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            with urllib.request.urlopen(f"https://fonts.gstatic.com/s/e/notoemoji/latest/{cps}/512.png", timeout=60) as r:
                dest.write_bytes(r.read())
        except Exception as e:  # noqa: BLE001
            die(f"could not download emoji {emoji} ({e})")
    return Image.open(dest).convert("RGBA")


def find_font(name: str):
    want = name.lower().replace(" ", "").replace("-", "")
    for f in font_files():
        if f.stem.lower().replace("-", "").startswith(want):
            return f
    die(f"font '{name}' not found in fonts/ (try: python tools/get_fonts.py \"{name}\")")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--emoji", required=True)
    ap.add_argument("--color", default="#8E44AD")
    ap.add_argument("--sub", default="")
    ap.add_argument("--corner-emoji", default="")
    ap.add_argument("--font", default="Poppins-800")
    ap.add_argument("--out")
    args = ap.parse_args()
    from PIL import Image, ImageDraw, ImageFilter, ImageFont

    col = tuple(int(args.color.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    c, r = S // 2, int(S * 0.40)
    # soft drop shadow
    sh = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((c - r, c - r + 14, c + r, c + r + 14), fill=(0, 0, 0, 120))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)))
    d = ImageDraw.Draw(img)
    # white disc with a subtle tint of the colour at the bottom
    disc = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    grad = Image.new("RGBA", (S, S))
    for y in range(S):
        k = max(0.0, (y - c) / r) * 0.10
        grad.paste((int(255 - (255 - col[0]) * k), int(255 - (255 - col[1]) * k), int(255 - (255 - col[2]) * k), 255), (0, y, S, y + 1))
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).ellipse((c - r, c - r, c + r, c + r), fill=255)
    disc.paste(grad, (0, 0), m)
    img.alpha_composite(disc)
    ring = int(r * 0.13)
    d.ellipse((c - r, c - r, c + r, c + r), outline=col + (255,), width=ring)
    # emoji
    em = emoji_png(args.emoji).resize((int(r * 0.95),) * 2, Image.LANCZOS)
    img.alpha_composite(em, (c - em.width // 2, c - int(r * 0.78)))
    # label (shrinks to fit)
    font_path = find_font(args.font)
    size = int(r * 0.36)
    while size > 10:
        f = ImageFont.truetype(str(font_path), size)
        if d.textlength(args.label, font=f) <= r * 1.3:
            break
        size -= 2
    y = c + int(r * (0.24 if args.sub else 0.32))
    d.text((c, y), args.label, font=f, fill=(25, 25, 35, 255), anchor="mm")
    if args.sub:
        ss = int(size * 0.5)
        while ss > 8:
            fs = ImageFont.truetype(str(font_path), ss)
            if d.textlength(args.sub, font=fs) <= r * 1.05:
                break
            ss -= 1
        d.text((c, y + int(size * 0.62) + ss // 2), args.sub, font=fs, fill=col + (255,), anchor="mm")
    if args.corner_emoji:
        ce = emoji_png(args.corner_emoji).resize((int(r * 0.5),) * 2, Image.LANCZOS)
        img.alpha_composite(ce, (c + int(r * 0.45), c - int(r * 0.95)))
    img = img.crop(img.getbbox())
    slug = re.sub(r"[^a-z0-9]+", "-", args.label.lower()).strip("-")
    dest = REPO / args.out if args.out else EDITS / "Raw" / args.project / f"badge-{slug}.png"
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest)
    print(f"Badge: {dest.relative_to(REPO)}")


if __name__ == "__main__":
    main()
