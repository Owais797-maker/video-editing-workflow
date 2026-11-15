# Style: bold-clean (DEFAULT)

The owner's standing preferences (2026-11-15):
- **Keep the video clean.** Don't pile things on top. What the video shows stays the hero.
- **Captions must be attractive, not basic**: bold modern fonts (Poppins, Anton and similar
  trending reel fonts), not thin or plain text.
- **Good SFX** where they help (cuts, pop-ups, key facts), never noisy.
- Product cutouts and small icon badges pop up only when that thing is mentioned.
- Extra effects (liquid glass etc., see `styles/liquid-glass/`) only when the owner asks.

## Captions
- Poppins ExtraBold, white, 2–3 words, lower-middle of the frame (y 0.70).
- The word being spoken turns **gold (#FFD400)** and grows 12%; each line pops in.
- Thin dark outline with a soft glow, so it reads on any background (even white packaging).
- Brand / product names as `captions.keywords` in **Anton gold, uppercase, bigger**, e.g.
  `"keywords": {"heavy": {"font": "Anton", "color": "#FFD400", "size": 6.6, "uppercase": true}, "gold": {...}}`.
- Roman Urdu, natural spelling; English words as spoken.

## Emphasis titles (sparingly: hook, maybe one punchline)
`segments` with presets: `small` (Poppins SemiBold italic), `serif` (Playfair Display
ExtraBold italic), `heavy` (Anton, gold, caps).

## Product moments
- Product cutout (`tools/cutout.py`) with `"animation": "rise"` (rises from the bottom)
  when the product is named; ~30% of the frame width; pair with `swoosh_up` + `pop` SFX.
- Icon badges (`tools/badge.py`) for ingredients/features as they are said, ~22% width,
  upper part of the frame, `pop` SFX each.
- Ending: `backdrop` (blur + dim) and the product cutout big in the centre.

## Pacing
Keep the speaker's natural rhythm, cut pauses and mistakes; gentle push-in on every shot,
punch-in on key words.
