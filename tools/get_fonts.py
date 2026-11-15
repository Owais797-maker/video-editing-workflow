#!/usr/bin/env python3
"""Download free (Open Font License) Google Fonts into fonts/.

    python tools/get_fonts.py                      # the standard set below
    python tools/get_fonts.py "Lobster" "Oswald:400,700" --folder "Bold Display Fonts"
    python tools/get_fonts.py "Poppins:500i,900"      # i = italic

Fonts already downloaded are skipped.
"""
import argparse
import re
import urllib.request

from common import FONTS, REPO, die

# folder -> {family: weights}
STANDARD = {
    "Urdu Fonts": {"Noto Nastaliq Urdu": "400,700", "Gulzar": "400", "Noto Naskh Arabic": "400,700"},
    "Subtitle Fonts": {"Poppins": "400,600,800,900,500i,600i", "Montserrat": "500,800", "Roboto": "400,700"},
    "Bold Display Fonts": {"Bebas Neue": "400", "Anton": "400", "Archivo Black": "400"},
    "Social Media Fonts": {"Luckiest Guy": "400", "Bangers": "400"},
    "Cinematic Fonts": {"Cinzel": "400,700", "Playfair Display": "400,700,600i,800i", "DM Serif Display": "400i"},
}
UA = "Mozilla/4.0"  # an old agent makes Google Fonts send plain .ttf files


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def download(family: str, weights: str, folder: str) -> int:
    """weights: "400,700" or with italics "500i,900" (i = italic)."""
    dest_dir = FONTS / folder
    pairs = sorted({(1 if w.strip().endswith("i") else 0, int(w.strip().rstrip("i"))) for w in weights.split(",")})
    q = family.replace(" ", "+") + ":ital,wght@" + ";".join(f"{i},{w}" for i, w in pairs)
    try:
        css = fetch(f"https://fonts.googleapis.com/css2?family={q}").decode()
    except Exception as e:  # noqa: BLE001
        print(f"  !! {family}: not found on Google Fonts ({e})")
        return 0
    got = 0
    for style, weight, url in re.findall(r"font-style:\s*(\w+);\s*font-weight:\s*(\d+);.*?src:\s*url\(([^)]+\.ttf)\)", css, re.S):
        name = f"{family.replace(' ', '')}-{weight}{'i' if style == 'italic' else ''}.ttf"
        dest = dest_dir / name
        if dest.exists():
            continue
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(fetch(url))
        print(f"  + {dest.relative_to(REPO)}")
        got += 1
    return got


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("families", nargs="*", help='e.g. "Lobster" or "Oswald:400,700"')
    ap.add_argument("--folder", default="Extra Fonts")
    args = ap.parse_args()
    if args.families:
        todo = {args.folder: {}}
        for f in args.families:
            fam, _, w = f.partition(":")
            todo[args.folder][fam.strip()] = w or "400"
    else:
        todo = STANDARD
    total = 0
    for folder, fams in todo.items():
        for fam, weights in fams.items():
            if weights:
                total += download(fam, weights, folder)
    print(f"{total} new font files in {FONTS.relative_to(REPO)}/" if total else "Nothing new to download.")


if __name__ == "__main__":
    try:
        main()
    except OSError as e:
        die(f"download failed: {e}. Check your internet connection.")
