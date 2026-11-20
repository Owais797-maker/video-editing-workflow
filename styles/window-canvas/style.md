# Style: window-canvas (owner, 2026-11-20: "next video mein yeh style")

Reference: https://www.instagram.com/reel/Df7o6-dStLS/ (reference-frame.jpg, reference-sheet.jpg).
Layout seen: soft light-blue gradient canvas (#EAF7FD → #9FDDF2); a BIG rounded video window on the right
(x 0.37–0.92, y 0.12–0.66) overlapping a SMALL window on the left (x 0.08–0.37, y 0.33–0.66), each with a
yellow pill label above (#FFC53D, black Poppins SemiBold: "Before" / "After"); a dark panel under the windows;
inside the big window: the edited video with designed captions and pop-in graphics (thumbnails, icons, chips).

Owner's version:
- The light/white canvas area carries an ILLUSTRATION (owner: "jo white hai wahan illustration de dena"):
  use an image the owner sends, the product mockup, or an illustration we make (line-art cattle/goat, farm,
  feed bag); keep it light so the windows stay the hero.
- The edited video plays in the window(s) ("jo sub window hai us mein video edit kar dena"); captions and
  graphics inside the big window (glow-stack or the current caption style).
- Labels in the owner's world: e.g. "پہلے / اب", "Dispatch / Customer", "Raw / Edit"; red/yellow pills with
  Urdu text (tools/urdu_text.py) are fine.

How to build with our tools:
- `frames` with `"bg": "image", "bg_file": "<illustration>.png"` (or `"bg": "gradient"`), `"scale": 0.55`,
  `"left": 0.37, "top": 0.12`, `"radius": 0.03` for the big window.
- Small second window (picture-in-picture of another clip/moment) is not built yet: add a second-window option
  to `frames` when making the first video in this style (or use one big window + an illustration).
- Labels: small PNG pills (urdu_text --plate yellow, or a Poppins pill) as overlays above each window.
