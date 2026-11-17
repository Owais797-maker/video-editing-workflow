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

## LOCKED HOUSE LOOK (owner, 2026-11-17: "is style ko lock kar do")
Every new video uses this without the owner explaining it again. Reference project:
`Video Edits/Export/heavy-gold-khanpur/edit.json` (copy its structure).

1. **Captions**: box-pop (Montserrat Black caps, spoken word in a rounded box in the product
   accent, `ink` = product dark colour), y 0.70, Roman Urdu, soft swish per line, whoosh on big words.
2. **Hook (0–1.5 s)**: map card Karachi → destination city whenever a city is said
   (`trr` SFX while the line draws + `click` on the pin), else a big glass widget.
3. **Boxes / headings = liquid-glass widgets** (styles/liquid-glass/widget-ref.jpg): smoky dark
   glass, thin light border, coloured dot + small label, big white Inter Tight Black value, small
   sub line. Just write `{"label","value","sub","dot","x","y","start","end"}`: the rest comes from
   `glass.widget` in style.json. Two-line value: `h` ≈ 0.3, `w` 0.72, `value_size` 0.24.
   Dot colours: product accent first, then blue #2F6BFF / green #3BD16F ("✓ Dispatched") / red #E8553B.
   Keep labels short (≤ 20 chars) so they stay inside the box. 1 widget at a time, upper third.
4. **Product**: BiRefNet cutout rising in (`rise`) on a grey round liquid-glass disc
   (`glass` with only x/y/w/h → `glass.plain`, radius 0.5) when the product is named;
   icon badges for features as spoken; END = backdrop blur + disc + cutout + final widget.
5. **Customer / dispatch reels**: widgets "<NAME> KA MAAL" (label "Karachi → City", sub
   "Product · N bags"), "<Name>" (label Customer), the customer's own words as a widget
   (e.g. SHAUQEEN), end "<NAME> · <CITY>" (label "✓ Dispatched").
6. **SFX** (under the voice, 0.25–0.5): impact on hook, trr + click on map, whoosh on each
   widget, swoosh_up + pop on cutout, pop on badges, ching/ding on key facts, riser before the end.
7. **Effects**, lightly: blur_whip on the cut into the product, one light_leak, one glitch on a punch word.
8. **Look**: crisp light cinematic, zoom_in + punch-ins, everything in the safe zone, CRF 17.
9. Always: caption review page → storyboard → OK → Full HD final → TikTok + Facebook copy.
