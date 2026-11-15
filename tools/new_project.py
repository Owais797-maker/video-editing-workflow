#!/usr/bin/env python3
"""Create the folders and brief for a new editing project.

    python tools/new_project.py my-reel

Creates:
    Video Edits/Raw/my-reel/          <- put your footage + music here
    Video Edits/Reference/my-reel/    <- put inspiration videos here
    Video Edits/Reference/my-reel/brief.md
    Video Edits/Export/my-reel/       <- storyboard, edit.json and final video go here
"""
import argparse
import re

from common import EDITS, REPO, die


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("name", help="project name, e.g. eid-reel (letters, numbers, - and _)")
    name = ap.parse_args().name.strip()
    if not re.fullmatch(r"[\w\-]+", name):
        die("use only letters, numbers, '-' and '_' in the project name")

    for sub in ("Raw", "Reference", "Export"):
        (EDITS / sub / name).mkdir(parents=True, exist_ok=True)
    brief = EDITS / "Reference" / name / "brief.md"
    if not brief.exists():
        text = (EDITS / "BRIEF_TEMPLATE.md").read_text(encoding="utf-8").replace("<project>", name)
        brief.write_text(text, encoding="utf-8")
    print(f"Project '{name}' ready:")
    for sub in ("Raw", "Reference", "Export"):
        print(f"  {(EDITS / sub / name).relative_to(REPO)}/")
    print(f"  {brief.relative_to(REPO)}  <- fill this in")


if __name__ == "__main__":
    main()
