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

## LOCKED HOUSE LOOK v2 (owner, 2026-11-18: "maza aa gaya, yeh pattern lock kar do")
Every new video is made in THIS mood without the owner explaining it again. Master reference:
`Video Edits/Export/three-products/edit.json` (copy its structure; preview
`Video Edits/Export/three-products/storyboard/frames.jpg`). Older dark-glass version:
heavy-gold-khanpur (widgets with `"theme": "dark"`).

1. **4K output** (2160×3840, style default): all graphics are drawn at 4K, razor sharp. Tell the
   owner to shoot in 4K for the sharpest footage. CRF 17 slow. If the file is too big to send, CRF 20.
2. **Grade**: bright, colourful, clean (cinematic 0.6, saturation 1.22, brightness +0.03,
   contrast 1.06, sharpen, grain 2). The VIDEO is colourful; the boxes stay calm.
3. **Captions**: box-pop, spoken word in a **white box with black text** (accent #FFFFFF,
   ink #111), Montserrat Black caps, y 0.70, Roman Urdu, soft swish per line, whoosh on big words.
   Mark every word of a name separately (`*Dil* *Murad*`), no punctuation glued to `*word*`.
4. **Hook (0–1.5 s)**: map card Karachi → city whenever a city is said ("*City* ka maal",
   `trr` + `click`), else a big widget.
5. **Boxes = light liquid-glass widgets**: frosted WHITE glass, thin white border, coloured dot
   + small label (Inter Tight), big black **Anton** value, sub line in Instrument Serif italic grey.
   Just write `{"label","value","sub","dot","x","y","w","start","end"}`; the rest comes from
   `glass.widget`. `w` 0.5 for one word, 0.72–0.8 for a name. No sub → `h` 0.15.
   Dot = that product's colour (Heavy Gold blue #1E3FA0, Mega-VMix red #E32626, Hepta Sef purple
   #8E2A9B, vaccines blue #1E88E5, gold #FFD400 for our team, green #3BD16F for "✓ done").
   Never over a face (put it on the chest / upper third). Labels ≤ 20 chars.
6. **Products**: when a product is SAID (or clearly shown if it isn't said) its mockup cutout
   rises in on a round clear glass disc (`glass` with only x/y/w/h, radius 0.5) + `pop` SFX.
   Several products named quickly → side by side discs (x .29 / .71). Cutouts live in
   `Video Edits/Raw/<product>/…-cutout.png` (Heavy Gold, Mega-VMix, Mega-Tox, Butter Milk,
   Hepta Sef in three-products/).
7. **People**: ASK who each person is before naming them (customer vs our team). Our team →
   widget label "Dispatch by", sub "Karachi → City". Customer → label "Customer · City".
8. **Ending (last ~2 s)**: backdrop blur, a wide clear glass panel (w .9 h .27 radius .12) with
   all products in a row, widget on top "<CUSTOMER> SAHAB" label "✓ <City> order", sub products.
9. **SFX** (0.25–0.5, under the voice): impact on hook, trr + click on map, whoosh into widgets,
   swoosh_up + pop per product, ching on a key word, whoosh + impact into the end, ding last.
10. **Effects** lightly: blur_whip into the hook and the end, one light_leak, one glitch on a punch word.
11. Always: caption review page → storyboard frames → OK → 4K final → offer TikTok + Facebook copy.
