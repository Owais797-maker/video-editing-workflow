#!/usr/bin/env python3
"""Free stock library of animals (cows, dairy cows, goats, calves...) for b-roll / motion-graphic inserts.

Source: Wikimedia Commons (only CC0 / public domain / CC-BY, i.e. free to use in the owner's videos;
credit CC-BY authors in the post if possible). Pexels / Pixabay block cloud downloads.

    python3 tools/stock.py fetch              # download everything in assets/stock/library.json (skips existing)
    python3 tools/stock.py search "Sahiwal cow" --kind photo --cat dairy-cow --min 1920 --limit 8   # add new items
    python3 tools/stock.py list               # what we have

Files land in assets/stock/<cat>/ (media is git-ignored); library.json (committed) keeps the url, licence and
author of every item so any future session can re-download the same library with `fetch`.
"""
import argparse
import json
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LIB = REPO / "assets" / "stock"
INDEX = LIB / "library.json"
API = "https://commons.wikimedia.org/w/api.php"
UA = "video-editing-workflow/1.0 (stock library script)"
OK_LIC = re.compile(r"^(cc0|cc-zero|public domain|pd|cc by \d|cc-by-\d|cc by-\d)", re.I)


def get(url: str) -> bytes:
    for i in range(6):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except Exception as e:  # 429 / transient
            if i == 5:
                raise
            time.sleep(10 * (i + 1))
    return b""


def api(**q) -> dict:
    q.update(format="json")
    return json.loads(get(API + "?" + urllib.parse.urlencode(q)))


def load() -> list:
    return json.loads(INDEX.read_text(encoding="utf-8")) if INDEX.exists() else []


def save(items: list) -> None:
    LIB.mkdir(parents=True, exist_ok=True)
    INDEX.write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")


def search(term: str, kind: str, cat: str, min_w: int, limit: int) -> None:
    items = load()
    have = {i["title"] for i in items}
    ft = "filetype:video" if kind == "video" else "filetype:bitmap"
    res = api(action="query", list="search", srsearch=f"{term} {ft}", srnamespace=6, srlimit=50)
    titles = [x["title"] for x in res["query"]["search"] if x["title"] not in have]
    added = 0
    for k in range(0, len(titles), 20):
        info = api(action="query", titles="|".join(titles[k:k + 20]), prop="imageinfo",
                   iiprop="url|size|extmetadata|mediatype", iiurlwidth=3840)
        for p in info["query"]["pages"].values():
            ii = (p.get("imageinfo") or [{}])[0]
            md = ii.get("extmetadata", {})
            lic = md.get("LicenseShortName", {}).get("value", "")
            w = ii.get("width", 0)
            if not ii or w < min_w or not OK_LIC.match(lic.strip()) or "-sa" in lic.lower() or " sa" in lic.lower():
                continue
            if kind == "video" and ii.get("duration", 99) and ii.get("duration", 0) and ii["duration"] > 120:
                continue
            author = re.sub("<[^>]+>", "", md.get("Artist", {}).get("value", "")).strip()[:80]
            url = ii["url"] if kind == "video" or w <= 3840 else ii.get("thumburl", ii["url"])
            items.append({"title": p["title"], "cat": cat, "kind": kind, "url": url, "width": w,
                          "height": ii.get("height", 0), "license": lic, "author": author,
                          "page": ii.get("descriptionurl", "")})
            added += 1
            print(f"+ {cat}: {p['title']}  {w}x{ii.get('height')}  {lic}  {author}")
            if added >= limit:
                break
        if added >= limit:
            break
    save(items)
    print(f"{added} added ({term})")


def fname(it: dict) -> Path:
    stem = re.sub(r"[^A-Za-z0-9]+", "-", it["title"].split(":", 1)[1].rsplit(".", 1)[0]).strip("-")[:60].lower()
    ext = "mp4" if it["kind"] == "video" else "jpg"
    return LIB / it["cat"] / f"{stem}.{ext}"


def fetch() -> None:
    for it in load():
        out = fname(it)
        if out.exists():
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        raw = out.with_suffix(".src")
        url = it["url"]
        if it["kind"] == "photo" and "/thumb/" not in url:  # Commons refuses bulk originals: use a standard thumb size
            px = 3840 if it["width"] >= 3840 else 1920
            base, name = url.rsplit("/", 1)
            url = base.replace("/commons/", "/commons/thumb/") + f"/{name}/{px}px-{name}"
            if name.lower().endswith((".tif", ".tiff")):
                url = base.replace("/commons/", "/commons/thumb/") + f"/{name}/lossy-page1-{px}px-{name}.jpg"
        try:
            raw.write_bytes(get(url))
        except Exception as e:
            print(f"skip {it['title']}: {e}")
            continue
        time.sleep(2)
        if it["kind"] == "video":  # webm/ogv -> high-quality mp4 that render.py reads fast, no audio
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-an", "-c:v", "libx264", "-crf", "16",
                            "-preset", "slow", "-pix_fmt", "yuv420p", str(out)], check=True)
        else:
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-q:v", "2", str(out)], check=True)
        raw.unlink()
        print(f"got {out.relative_to(REPO)}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search")
    s.add_argument("term")
    s.add_argument("--kind", choices=["photo", "video"], default="photo")
    s.add_argument("--cat", required=True)
    s.add_argument("--min", type=int, default=1920, help="minimum width in px")
    s.add_argument("--limit", type=int, default=8)
    sub.add_parser("fetch")
    sub.add_parser("list")
    a = ap.parse_args()
    if a.cmd == "search":
        search(a.term, a.kind, a.cat, a.min, a.limit)
    elif a.cmd == "fetch":
        fetch()
    else:
        for it in load():
            print(f"{it['cat']:12} {it['kind']:5} {it['width']}x{it['height']}  {it['license']:12} {fname(it).name}")


if __name__ == "__main__":
    sys.exit(main())
