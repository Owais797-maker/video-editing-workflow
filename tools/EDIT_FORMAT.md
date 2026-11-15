# edit.json format

`Video Edits/Export/<project>/edit.json` describes the whole edit. `storyboard.py`
and `render.py` both read it, so the approved storyboard is exactly what gets rendered.

Times are in seconds. `src` and `music.file` are looked up in `Raw/<project>/`,
then `Reference/<project>/`, then the repo root.

```json
{
  "project": "eid-reel",
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
      "transition": { "type": "fade", "duration": 0.3 }
    }
  ],

  "texts": [
    { "text": "عید مبارک\nEID MUBARAK", "start": 0, "end": 2.5, "position": "top",
      "size": 6, "color": "#FFFFFF", "font": "Noto Nastaliq Urdu",
      "bold": true, "box": false, "box_color": "#000000", "animation": "pop" }
  ],

  "captions": {
    "file": "captions.json", "words_per_line": 3, "max_gap": 0.6,
    "style": { "font": "Montserrat", "size": 4.5, "color": "white", "highlight_color": "#FFE600",
               "position": "bottom", "margin": 18, "uppercase": false, "box": false }
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

**texts** – titles and other on-screen text, timed on the final video. `\n` = new line.
`position`: top / center / bottom. `size`: percent of the video height. `animation`: fade / pop / none.
`font`: the font *name* (`python tools/check_setup.py` lists them), not the file name.

**captions** – built by `tools/captions.py` from Whisper transcripts into `captions.json`,
which can be corrected by hand. `highlight_color` colours the word being spoken.
Urdu and other right-to-left text is shaped correctly as long as the font supports it.

**music** – loops if shorter than the video. `duck` lowers it while people speak.

**look** – simple colour adjustment (`eq`), and/or a `.cube` LUT file.

**loudness** – target LUFS for the final mix (-14 suits social media). `null` turns it off.
