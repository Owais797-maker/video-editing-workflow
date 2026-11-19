# Typography & design skill: minimal, professional, elegant

Read this BEFORE putting any text or graphic on a video. Owner's verdict (2026-11-19) on a gym edit:
"basic fonts, font design not right, looks like a child edited it". Design so this never happens again.

## 0. Mindset
- Design is decisions, not decoration. Every element needs a reason. If removing it doesn't hurt, remove it.
- The footage is the hero. Text is a quiet, confident voice: fewer words, better set.
- "AI look" = default fonts, centred everything, random sizes, drop shadows everywhere, too many effects,
  generic quotes. "Human/pro look" = a clear idea, a tight grid, considered type, restraint, one surprise.

## 1. Start from an IDEA, then a palette
1. Find the story/idea in the footage itself (a sign on the wall, the product, a place, an outfit).
2. Palette = 3 colours max, sampled from the frame (`ffmpeg` frame → pick): one neutral (off-white
   #EDE9E0 / near-black #111), one main (outfit/product colour), one small accent. Never pure #FFFFFF
   on warm footage: use warm off-white. Accent ≤ 10% of the text.
3. One graphic motif taken from the subject (stripes from track pants, the product's badge shape, a
   line from the logo) used at most twice. That is what makes it look designed, not templated.

## 2. Type pairing (max 2 families, 3 weights)
Pick ONE pairing per video and stick to it:
| Mood | Display (headline) | Support (small text) |
|---|---|---|
| Sport / gym / energy | Big Shoulders Display Black, Anton (condensed caps) | Barlow Condensed SemiBold Italic, Inter Tight |
| Elegant / premium / lifestyle | Instrument Serif (italic for one word) | Inter Tight 600–800 |
| Editorial / magazine | Playfair Display 800 Italic | Inter Tight / Poppins SemiBold |
| Clean product / tech | Inter Tight 900 | Inter Tight 600 |
| Friendly / social | Poppins 700–800 | Poppins SemiBold |
| Street / bold reel | Montserrat Black caps | Yellowtail script (one word only) |
Rules: serif + sans or condensed + regular, never two similar sans. Script fonts: one word, never a sentence.

## 3. Hierarchy & scale (sizes as % of frame height, 9:16)
- Three levels only: **Hero** 8–14% (1–3 words), **Support** 2.4–3.4%, **Micro label** 1.6–2.2%.
- Size jumps must be obvious (≥ 2.5×), never 10% / 12% / 14% steps that look accidental.
- Micro labels: CAPS + tracking (spacing 4–8) + lighter colour. Heroes: tight tracking (0 to -1), never spaced.
- Line height for stacked caps ~0.9; don't let lines touch or float apart.

## 4. Layout & grid
- Margins: left/right 8% of width, all text on ONE left edge (x 0.08) for a film/editorial look, or
  perfectly centred; never mix alignments in one video.
- Keep everything in the safe zone (top 12%, bottom 25%, left 6%, right 14%).
- Place text in negative space (walls, ceiling, floor), never across faces, hands, or the action.
- Group related lines (label + hero + sub) as one block with consistent internal spacing; leave big
  empty space around the block.
- Max 2 text events on screen at once; most of the video should be clean footage.

## 5. Treatments that look expensive
- Hollow (outline) + solid pairing: `"hollow": true, "stroke": 2–2.6` on one word ("DAY" hollow, "ONE." solid).
- Crystal-clear glass card (`glass` with `"crystal": true`): no frost, sheen + rim, for a name/credit
  card; text white, display font for the value, condensed italic for label/sub.
- Letterbox bars (6–7%), soft vignette, grain 3–4, teal/warm grade for cinema; light grade for products.
- Subtle motion only: slide_up 4–6%, fades 200–300 ms, one pop at most. No bouncing everything.
- Shadows: soft and low (or none on clean backgrounds). Never thick black outlines on elegant work.

## 6. Words
- Write like a human: short, specific, a little personal. Use the subject's own world ("ONE DAY or DAY
  ONE", the wall sign), not motivational clichés.
- English titles: sentence case or CAPS consistently; full stop on a hero for attitude ("DAY ONE.").

## 7. Critique before showing the owner (must pass all)
1. Can you say the idea in one sentence? 2. Do the fonts match the subject's mood and the palette match the
frame? 3. Three clear size levels? 4. One alignment, consistent margins? 5. Nothing on faces/action,
all in the safe zone? 6. Would a top agency ship it, or does anything look default/templated?
7. Look at a FULL-RES frame (not only thumbnails) for spacing, kerning, overlaps, colour.
If any answer is no, fix it first. Show the owner 2 directions (e.g. "sport condensed" vs "elegant serif")
as stills when the brief is open, then build the chosen one.

## 8. Tools here
- Text segments: font, size, italic, color, spacing, hollow/stroke, newline; `"align": "left"`.
- Glass: `crystal`, `label_font`, `value_font`, `sub_font`, `text_color`, widgets.
- Caption templates: clean, pill, box-pop, minimal, editorial, swiss, script-mix…
- Fonts: fonts/README.md; add any Google Font with tools/get_fonts.py and commit it.
