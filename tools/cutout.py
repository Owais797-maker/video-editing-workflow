#!/usr/bin/env python3
"""Cut a product (bag, box, bottle ...) out of its background, for use as a sticker overlay.

    python tools/cutout.py "Video Edits/Raw/my-reel/product.jpg"
        -> Video Edits/Raw/my-reel/product-cutout.png (transparent background)

Uses the BiRefNet model (via rembg), which keeps real edges, strings and folds and
handles white packaging well. Gaps fully enclosed by the product are filled
(--keep-holes keeps them, for products with real holes such as a handle), and
stray specks are dropped. The first run downloads the model (~900 MB).
"""
import argparse

from common import die, resolve


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image")
    ap.add_argument("--out")
    ap.add_argument("--keep-holes", action="store_true")
    ap.add_argument("--model", default="birefnet-general",
                    help="birefnet-general (best, default), isnet-general-use (faster), u2net")
    args = ap.parse_args()
    try:
        import numpy as np
        from PIL import Image
        from rembg import new_session, remove
        from scipy import ndimage as ndi
    except ImportError:
        die("missing packages. Run: pip install -r requirements.txt")

    src_path = resolve(args.image)
    if not src_path.exists():
        die(f"file not found: {src_path}")
    im = Image.open(src_path).convert("RGB")
    cut = remove(im, session=new_session(args.model))
    alpha = np.array(cut.split()[-1])
    if (alpha > 128).sum() == 0:
        die("could not find a product in this image")
    solid = alpha > 128
    lab, n = ndi.label(solid)
    if n > 1:  # keep the product, drop stray specks (anything under 1% of the largest piece)
        sizes = ndi.sum(solid, lab, range(1, n + 1))
        keep = [i + 1 for i, sz in enumerate(sizes) if sz >= 0.01 * sizes.max()]
        alpha = np.where(np.isin(lab, keep) | ((alpha <= 128) & (alpha > 0)), alpha, 0)
    if not args.keep_holes:  # make see-through areas inside the product solid
        filled = ndi.binary_fill_holes(alpha > 128)
        alpha = np.where(filled & (alpha <= 128), 255, alpha)
    alpha = Image.fromarray(alpha.astype(np.uint8))
    out = im.convert("RGBA")
    out.putalpha(alpha)
    out = out.crop(out.getbbox())
    dest = resolve(args.out) if args.out else src_path.with_name(src_path.stem + "-cutout.png")
    out.save(dest)
    print(f"Cutout: {dest} ({out.width}x{out.height})")


if __name__ == "__main__":
    main()
