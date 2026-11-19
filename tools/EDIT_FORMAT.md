# edit.json format

`Video Edits/Export/<project>/edit.json` describes the whole edit. `storyboard.py`
and `render.py` both read it, so the approved storyboard is exactly what gets rendered.

Times are in seconds. `src` and `music.file` are looked up in `Raw/<project>/`,
then `Reference/<project>/`, then the repo root.

```json
{
  "project": "eid-reel",
  "style": "reels-bold",
  "title": "Eid Reel",
  "summary": "One or two lines: what this video is and its story.",
  "reference_notes": "What was taken from the reference: pacing, captions, transitions, look.",

  "output": { "width": 1080, "height": 1920, "fps": 30, "fit": "crop" },

  "shots": [
    {
      "src": "clip1.mp4", "in": 12.0, "out": 15.5,
      "description": "Hook: close-up of the sweets",
      "speed": 1.0, "zoom": 1.0, "focus_x": 0.5, "focus_y": 0.5,
      "fit": "crop", "volume": 1.0, "mute": false, "no_captions": false,
      "transition": { "type": "fade", "duration": 0.3 },
      "motion": { "type": "zoom_in", "amount": 0.1 },
      "punch": [[1.2, 1.8]], "punch_zoom": 1.15,
      "shake": [[0.0, 0.4]], "shake_amount": 14
    }
  ],

  "texts": [
    { "text": "عید مبارک\nEID MUBARAK", "start": 0, "end": 2.5, "position": "top",
      "size": 6, "color": "#FFFFFF", "font": "Noto Nastaliq Urdu",
      "bold": true, "box": false, "box_color": "#000000", "animation": "pop" }
  ],

  "overlays": [
    { "emoji": "🔥", "animated": true, "start": 1.0, "end": 3.0, "position": "top-right", "width": 0.18, "animation": "pop" },
    { "file": "logo.png", "start": 0, "end": 30, "position": "bottom-left", "width": 0.15, "animation": "fade" }
  ],
  "progress_bar": { "color": "#FFE600", "height": 10, "position": "top" },

  "captions": {
    "file": "captions.json", "words_per_line": 3, "max_gap": 0.6,
    "style": { "font": "Montserrat", "size": 4.5, "color": "white", "highlight_color": "#FFE600",
               "position": "bottom", "margin": 18, "uppercase": false, "box": false,
               "highlight_scale": 1.1, "animation": "pop" }
  },

  "music": { "file": "music.mp3", "start": 0, "volume": 0.25, "duck": true, "fade_in": 0, "fade_out": 2 },
  "look": { "brightness": 0.0, "contrast": 1.0, "saturation": 1.0, "gamma": 1.0, "lut": "luts/warm.cube" },
  "fade": { "in": 0.3, "out": 0.5 },
  "loudness": -14,
  "quality": { "crf": 18, "preset": "medium" }
}
```

## Fields

**output** – `fit` frames clips whose shape differs from the output:
`crop` fills the frame (cuts the sides), `blur` shows the whole clip over a blurred copy,
`pad` shows the whole clip with black bars. Common sizes: 1080x1920 (Reels/Shorts/TikTok),
1920x1080 (YouTube), 1080x1080 (square), 1080x1350 (4:5 feed).

**shots** (in order; only `src` is required)
- `in` / `out`: part of the source clip to use (default: whole clip).
- `speed`: 0.25–4 (sound changes speed too, pitch stays the same).
- `zoom`: punch-in, e.g. 1.15. `focus_x` / `focus_y`: 0 = left/top, 1 = right/bottom; picks which part stays when cropping.
- `fit`: override the output framing for this shot.
- `volume`, `mute`: original sound of this shot. `no_captions`: leave this shot out of the captions.
- `transition`: into the NEXT shot. `"cut"` (default) or an FFmpeg xfade name with a duration:
  `fade`, `fadeblack`, `fadewhite`, `dissolve`, `wipeleft`, `wiperight`, `slideleft`, `slideright`,
  `slideup`, `slidedown`, `circleopen`, `circleclose`, `radial`, `smoothleft`, `zoomin`, `pixelize`, `hblur`.
  A transition overlaps the two shots, so the video gets shorter by its duration.

**style** – name of a folder in `styles/` whose `style.json` fills in everything this
file doesn't set (see styles/README.md). Default: `styles/default.txt`. `null` = no style.
`"captions": true` means "captions in the style's caption look".

**texts** – titles and other on-screen text, timed on the final video. `\n` = new line.
`position`: top / center / bottom (or `x`, `y` as 0–1 fractions of the frame).
`size`: percent of the video height. `margin`: distance from the edge, percent of height.
`animation`: `fade`, `pop` (scales in with a bounce), `slide_up`, `slide_left`,
`typewriter` (words appear one by one), `none`.
`"type": "lower_third"` makes a name strip that slides in from the left:
`{"type": "lower_third", "text": "Owais", "subtext": "Video Creator", "start": 2, "end": 6,
"color": "#E91E63", "font": "Montserrat", "x": 0.06, "y": 0.64}`. The default position sits just above bottom captions.
`font`: the font *name* (`python tools/check_setup.py` lists them), not the file name.

**captions** – built by `tools/captions.py` from Whisper transcripts into `captions.json`,
which can be corrected by hand. `highlight_color` colours the word being spoken.
Urdu and other right-to-left text is shaped correctly as long as the font supports it.

**Motion on shots** – `motion.type`: `zoom_in`, `zoom_out` (slow push in/out over the
shot), `pan_left`, `pan_right`, `pan_up`, `pan_down` (zoomed in by `amount` and moving),
or `none`. `punch`: list of `[start, end]` seconds *within the shot* where the picture
jumps closer by `punch_zoom` (emphasis "zoom cut"). `shake`: `[start, end]` ranges of
camera shake (`shake_amount` in pixels). All are smooth, sub-pixel movement.

**overlays** – images and emoji over the video, timed on the final video. `file` (PNG with
transparency, from Raw/<project>/) or `emoji` (any emoji; Google's Noto emoji, downloaded
automatically; `"animated": true` uses the animated version). `position`: top-left, top,
top-right, left, center, right, bottom-left, bottom, bottom-right (or `x`, `y` fractions).
`width`: fraction of the video width. `animation`: `pop`, `fade`, `slide_up`, `rise`
(comes up from the bottom edge with a small overshoot), `none`.

**glass** – liquid-glass cards (frosted, blurred video behind, white border, rounded):
`[{"x": 0.5, "y": 0.2, "w": 0.72, "h": 0.09, "text": "Heavy Gold", "subtext": "5 in 1",
"start": 1, "end": 3.5, "radius": 0.28, "blur": 22, "tint": 0.10, "border": 0.55, "size": 3.6}]`.
Product-coloured glass: `"tint_color": "#2457C5", "tint": 0.35, "border_color": "#7FA6FF", "border_width": 3`.
Only on request (or in the product palette when the owner asks for boxes).

**captions.style.mode: "html"** – designer captions rendered with HTML/CSS in headless Chromium
(`tools/html_captions.py`, templates in `tools/htmlcaps/templates.css`): `"template"`: `box-pop`
(spoken word in a rounded accent box), `editorial` (small sans + big serif italic word),
`minimal` (whole line dim, spoken words light up), `outline-3d` (Anton with ink stroke and
extrusion), `press` (vintage letterpress ink), `glass` (frosted pill); `"accent"` colour, `"y"`.
Words pop in as spoken; `*big*` marks and keywords apply. Preview all templates on a frame:
`python tools/html_captions.py --showcase "<edit.json>" --at 12.4`. New looks = new CSS classes.

**glass widget** (owner's standard box, see styles/liquid-glass/widget-ref.jpg): a glass item with
`"label"`, `"value"`, `"sub"`, `"dot"` becomes an iOS-style liquid-glass widget (dot + small label,
big value, small line, left aligned). Standard look: `"tint_color": "#1C1C1E", "tint": 0.38,
"border_color": "#FFFFFF", "border": 0.38, "border_width": 2, "radius": 0.22, "blur": 24,
"brightness": -0.04, "saturation": 1.1, "value_font": "Inter Tight Black", "value_size": 0.4`.

**captions.keywords** – words styled differently whenever they appear in captions:
`{"heavy": {"font": "Anton", "color": "#FFD400", "size": 6.6, "uppercase": true}}`.
**captions.style.glow** – soft blur on the outline (e.g. 6) for a glow look; `outline_alpha`
makes the outline see-through (0 = solid, 255 = invisible).

**brand / cards / frame** – motion-graphics product inserts (tools/cards.py, style brand-cards):
`"brand": {"bg1": "#2453C8", "bg2": "#0B1E57", "accent": "#FFD400", "ink": "#0B1E57"}`;
`"cards"`: full-frame cards over the picture while the voice continues — `type` `headline`
(`label`, `title` with `*accent*` words and `\n`, `sub`, `product`), `stats` (`stats`:
[{value, tag}], `align: "left"`), `contact` (`title`, `lines`, `phones`, `small`); options
`product_size` (0–1 of width), `product_pos` (bottom, bottom-right, top, center), `stack_top`,
`theme`. `"frame": {"margin": 0.035, "top": 0.035, "radius": 44, "border": 9}` puts the video
inside a rounded accent-bordered card on the brand background.

**safe** – `{"top": 0.12, "bottom": 0.25, "left": 0.06, "right": 0.14}` (default in bold-clean):
the TikTok / Instagram Reels / WhatsApp Status safe zone. Captions, texts, glass boxes and card
text are kept inside it; storyboard frames show it as a cyan box.

**effects** – short picture effects: `[{"type": "light_leak", "at": 0.1, "dur": 0.9, "color": "#FF9A3C"},
{"type": "glitch", "at": 2.4, "dur": 0.2, "amount": 14}, {"type": "blur_whip", "at": 4.5, "dur": 0.15}]`.
Use them sparingly on hooks, cuts and punchlines.

**cards: section / tag** (Swiss-editorial, styles/swiss-editorial): `{"type": "section", "kicker": "part",
"number": "2", "bg": "#E10600"}` or `{"type": "section", "title": "Framing\n*and*\ncomposition",
"bg": "#EAF1FF", "light": true}` (the `*word*` sits on a red bar); `{"type": "tag", "text": "PROTEIN",
"color": "#5AD32F", "x": 0.46, "y": 0.3, "w": 0.5, "h": 0.075}` types its letters in over the video.
Caption template `swiss`: big tight lowercase words stacked at the top (`"y": 0.17`, words_per_line 1–2).

**Explainer UI** (styles/explainer-ui): `"frame": {"layout": "split", "split": 0.5}` puts the speaker in a
rounded card in the lower half; card `{"type": "panel", "area": "top-half" | "card", "steps": 5, "step": 2,
"label": "Tareeka #2", "pill": "Example", "text": "Janwar ka *wazan* kyun nahi barh raha?", "read_time": 2.4,
"light": false}` — words light up as spoken, `*word*` in accent serif italic. Caption template `explainer`.

**backdrop** – `[{"start": 17.6, "end": 20, "blur": 18, "dim": 0.35}]` blurs and darkens the
video for that time, e.g. behind a product cutout ("product card") or a big title.

**progress_bar** – a bar that fills across the top (or bottom) as the video plays.

**captions.style** – `highlight_scale` enlarges the word being spoken (1.1 = 10%);
`animation`: `pop` or `fade`. `italic`, `uppercase` / `lowercase`. `y` (0–1) places captions
at that height in the middle of the frame instead of using `position`. `outline` (0 = none),
`shadow` (depth in px), `shadow_color`, `shadow_alpha` (0 = solid, 255 = invisible).
The same `italic`, `outline`, `shadow*` keys work on texts.

**Mixed typography** – a text item can use `segments` instead of `text`: each segment has
its own `font`, `size`, `italic`, `bold`, `color`, `uppercase`/`lowercase`, or a `preset`
name from `type_presets` (usually defined by the style). `"newline": true` starts a new line; `"attach": true` joins a segment to the previous one with no space.
```json
{"segments": [{"text": "se zyada", "preset": "small"}, {"text": "8cr", "preset": "serif", "newline": true},
              {"text": "+", "preset": "heavy"}], "start": 0.3, "end": 3.0, "y": 0.5}
```

**sfx** – sound effects at exact times: `[{"sound": "whoosh", "at": 3.2, "volume": 0.5}]` with the
built-in sounds from `tools/sfx.py` (whoosh, whoosh_fast, swoosh_up, pop, click, keys = iPhone typing, ding, ching,
impact, boom, riser, glitch) or `{"file": "my-sound.wav", "at": ...}` from Raw/<project>/.

**music** – loops if shorter than the video. `duck` lowers it while people speak.

**look** – `cinematic` (0–1.5: S-curve contrast, teal shadows, warm highlights; keeps detail), `brightness`, `contrast`, `saturation`, `gamma` (eq), `warmth` (+ warmer / − cooler),
`sharpen` (0.3–0.8), `vignette` (angle, ~0.5), `grain` (film grain 3–6), and/or a `.cube` LUT.

**flashes** – `[{"at": 2.23, "alpha": 0.5, "dur": 0.18, "color": "white"}]` quick flash, e.g. on a cut.

**loudness** – target LUFS for the final mix (-14 suits social media). `null` turns it off.


Glass widget sub line styling: `sub_font` (default Inter Tight), `sub_italic`, `sub_size` (× label size), `sub_color`, `sub_spacing` (letter spacing px). Defaults come from the style's `glass.widget`.

**Icon tiles** (`tools/tile.py --project P --name vitamins --emoji 💊 --color "#1E4FA8"`): glossy app-icon tiles; pop them in a row (width ~0.135, x step 0.13) as each feature is spoken, with a typed `tag` card above and the `keys` SFX.

**frames** (timed semi-frame): `[{"start": 3.6, "end": 8.1, "scale": 0.84, "top": 0.09, "radius": 0.05, "bg": "lines" | "grid" | "hlines" | "blur", "bg_color": "#0B2560", "line_alpha": 0.07, "line_step": 0.045}]`: the video sits in a rounded white-bordered card over a plain colour background with soft lines (default; blur only on request).

**route card**: `{"type": "route", "from": "Karachi", "to": "Rawalpindi", "label": "Dispatch · Live", "title": "Karachi → Rawalpindi", "x": 0.46, "y": 0.3, "w": 0.76, "h": 0.3, "route_time": 0.75, "color": "#FF3B3B", "vehicle": "🚚"}`: floating live-tracking panel, truck drives along the route.

Caption lines in captions.json can carry `"y"` (0–1) to move just that line (e.g. off a face).
Caption template `pill`: Poppins on a frosted brand-colour pill (`"pill": "#1E3FA0"`, keywords in `accent`).

Texts: `"align": "left"|"right"` anchors the text block at x/y from its top-left/right corner; segments take `"spacing"` (letter spacing, px at 1080 wide).

Glass `"crystal": true`: crystal-clear lens glass (no frost, sheen + rim, slight magnify); `label_font` for widgets. Text segments: `"hollow": true, "stroke": 2.4` = outline letters.

Caption template `glow-stack` (layout `tier`): small white caps line + big glowing hero words; mark the first hero word with *word*.

**sfx** extras: any earshot bank id works as a sound name (`"sound": "whoosh_fast/crisp"`, `"pro_pop/bloop"`, list: `earshot sfx list`); `"sfx_bank": "pro"` (edit or style) upgrades the classic names (whoosh, pop, ding, keys, impact …) to earshot pro sounds.
