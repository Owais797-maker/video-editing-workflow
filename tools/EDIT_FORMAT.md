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
`width`: fraction of the video width. `animation`: `pop`, `fade`, `slide_up`, `none`.

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
name from `type_presets` (usually defined by the style). `"newline": true` starts a new line.
```json
{"segments": [{"text": "se zyada", "preset": "small"}, {"text": "8cr", "preset": "serif", "newline": true},
              {"text": "+", "preset": "heavy"}], "start": 0.3, "end": 3.0, "y": 0.5}
```

**music** – loops if shorter than the video. `duck` lowers it while people speak.

**look** – simple colour adjustment (`eq`), and/or a `.cube` LUT file.

**loudness** – target LUFS for the final mix (-14 suits social media). `null` turns it off.
