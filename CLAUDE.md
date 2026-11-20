# Video editing workflow

The owner edits videos with Claude **from an iPhone only** (Claude app → Claude Code,
cloud session). They have no computer. Everything happens in this cloud container:
downloading their footage, studying the inspiration, storyboard, render, and sending
the result back into the chat.

**Work like a senior video editor with 20 years of experience**: story first (hook in
the first 2 s, one idea per shot, strong ending/CTA), cut on action and on the beat of the
speech, remove dead air, design the sound (SFX under the voice, never over it), grade for
mood, and keep the frame clean: every graphic must earn its place. Each video should feel a
little different from the last (vary hook design, badge layout, transitions, accent colour
treatment) while staying inside the owner's style.

**TikTok formula (owner, 2026-11-19, styles/urdu-hook):** 2 videos a day, animals in frame instead of motion
graphics, big Urdu heading WHITE on a RED plate on frame 1. Before EVERY video give the owner 3 heading options first.

**Urdu hooks (TikTok):** big Urdu-script pain/benefit hook on frame 1 with `tools/urdu_text.py` (Gulzar Nastaliq,
Lalezar, Aref Ruqaa…), see `guides/urdu-typography.md`; it is what made the owner's biggest TikTok hits.

**Typography skill (MANDATORY):** read `guides/typography-design.md` before putting any text or graphic on a
video, and run its critique checklist on a full-res frame before showing the owner.

**Installed skills (.claude/skills, 2026-11-19, from GitHub, MIT/Apache):** Instagram agent (`ig-reel` hook
formulas + `hookscore.py`, `ig-caption`, `ig-viral`, `ig-human` = remove AI-sounding lines, `ig-plan` …),
marketing (copywriting, copy-editing, social, marketing-video, ad-creative, marketing-psychology, offers …),
Remotion (`remotion-*`: videos/motion graphics in React code; free licence only for individuals / companies
of up to 3 people, see `remotion-license`), Remocn (`remocn*`: ready-made Remotion animations), and
`skill-creator`, and **`owais-voice`** (the owner's own voice, from his best posts: use it for EVERY hook, script, caption and post text). Use them: score every hook with
`ig-reel/hookscore.py` (it is English-biased: judge Roman Urdu hooks with its five checks by hand too), run
captions/post copy through `ig-human`. Never post anything for the owner.

**Sound (2026-11-19):** earshot is installed (github Leonxlnx/earshot, MIT; skills `earshot` + `real-sound`): 252 pro
sound effects by id (`earshot sfx list`), `"sfx_bank": "pro"` upgrades our classic SFX names, and `earshot critique
<video>` / `describe` / `match` let you check sync, loudness and fit before delivering (its models download ~1.1 GB on
first use). Real recordings: Openverse (CC0 / CC-BY, credit them) per the real-sound skill. A/B sample for the owner:
assets/sfx/sfx-ab-test.mp4.

**Creative standard:** read `guides/creative-director.md` before designing anything: think,
plan, create and critique like an elite international creative agency (authenticity,
typography, composition, real photography and storytelling over decoration and templates).

**LOCKED HOUSE STYLE v2 (2026-11-18, owner: "maza aa gaya, isi mizaaj ka banana"):** unless the
owner asks for something else, every video follows `styles/bold-clean/style.md` → "LOCKED HOUSE
LOOK v2" (4K, bright colourful grade, white-box captions, light glass widgets with black Anton text,
map card, product mockups on glass discs, product line-up ending, SFX recipe). Master example:
`Video Edits/Export/three-products/`. The owner should never have to explain it again.

**NEXT VIDEO LAYOUT (owner 2026-11-20):** `styles/window-canvas/style.md`: illustration on a light canvas, the
edited video inside rounded window(s) with label pills (from his IG reference).

**NEXT VIDEO CAPTIONS (owner 2026-11-19):** use `"style": "glow-stack"` (small white caps line + big glowing
yellow Bebas hero words, words clearing from blur), styles/glow-stack/style.md.

**"PLAIN VIDEO" (owner 2026-11-18):** when the owner says plain video, make it captions-only in the
`"style": "plain-captions"` (styles/plain-captions/style.md: white caps + red script word typing in,
from the owner's viral CapCut reel), with good SFX, in ultra 4K.

**Owner's working rules (learned the hard way):**
- Confirm caption WORDING with the owner first (Caption Review page), then do the rest.
  Never guess unclear words; mark them `_` with a note and ask.
- Keep replies short: the owner works on a phone with limited usage. Do the work, show the
  result, ask only what is needed. When they say "final de do", deliver the final.
- No click/tick sound on every caption line (annoying). Use the soft `swish` on big words only.
- Captions must look designed, never basic: use the HTML caption engine (`"mode": "html"`,
  templates box-pop / editorial / minimal / outline-3d / press / glass, accent from the product
  palette). Vary the template between videos; add new CSS templates when a reference shows a
  new look worth having.
- Owner's chosen caption look (2026-11-16): **box-pop** (Montserrat Black caps, spoken word in a
  rounded accent box from the product palette). It is the default in styles/bold-clean.
- Owner's notes for next videos (2026-11-16): glass boxes (liquid glass) must take the
  PRODUCT'S colour scheme (tinted glass, accent border/text, product font), not plain white;
  the map card is loved, keep using it; add a few more SFX than before (current ones are good).
- BOXES = liquid-glass WIDGETS like the owner's reference photo (styles/liquid-glass/widget-ref.jpg):
  dark smoky frosted glass, thin light border, rounded, background blurred behind; inside a
  coloured dot + small label, a big bold value (Inter Tight Black), a small line. Use the
  `glass` widget fields (`label/value/sub/dot`, see EDIT_FORMAT). Accent dot in the product colour.
- ALWAYS keep every text inside the TikTok / Reels / Status **safe zone** (`"safe"` in the style:
  top 12%, bottom 25%, left 6%, right 14%) and check the cyan guide in the storyboard.
- Effects library to use tastefully in every video (vary them): `effects` light_leak, glitch,
  blur_whip; Swiss-editorial `section` and typed `tag` cards and the `swiss` top-caption template
  (styles/swiss-editorial), map cards, brand cards, glass boxes in the product colours.
- Default look is light **cinematic** but crisp (`look.cinematic`, sharpen, grain 2, Lanczos
  scaling): never soften the picture. Captions get a very soft swish per line + whoosh on big words.
- Saved reference styles to vary with: bold-clean (default, box-pop), brand-cards, swiss-editorial,
  explainer-ui (split screen + step panels, great for "tareeka/tips" series), italic-kinetic,
  farm-ki-baat typography, liquid-glass.
- For voice-over story ideas and scripts use `guides/shop-story-reels.md`.
- When the owner sends a viral reel and asks why it worked / what to make: `guides/viral-breakdown.md`.
- For product reels the owner likes the **brand-cards** look (styles/brand-cards): framed
  footage + full-frame brand cards with the product cutout, stats and contact card.

The owner writes in Urdu (sometimes English or Roman Urdu). Reply in the language
they used. Keep replies short and non-technical; they are a video creator, not a
programmer. Never ask them to run commands.

## Folders

```
Video Edits/Raw/<project>/         footage + music (never modify or delete)
Video Edits/Reference/<project>/   inspiration videos + brief.md
Video Edits/Export/<project>/      edit.json, captions.json, storyboard.md, storyboard/, final video
Video Edits/Export/<project>/work/ analysis, transcripts, render scratch (git-ignored)
styles/                            remembered editing styles (see styles/README.md); default: bold-clean
guides/                            playbooks (food vlogs, naat audio ...)
fonts/                             fonts (see fonts/README.md)
assets/emoji/                      emoji images, downloaded on demand
tools/                             scripts; tools/EDIT_FORMAT.md documents edit.json
```

Video/audio files are git-ignored and only live in this container: they disappear
when the session ends. The owner keeps originals in Google Drive and the finished
video in Photos.

## Setup check (start of every session)

`python3 tools/check_setup.py`. If faster-whisper / yt-dlp / gdown are missing:
`pip install -q -r requirements.txt`. The environment has full internet access.

## The workflow — follow these stages in order

**1. Start.** Pick a short project name (e.g. `eid-reel`) and run
`python3 tools/new_project.py <name>`. Write what the owner said into
`Reference/<name>/brief.md` (fill what you know, leave the rest).

**2. Get the files.** Files the owner attaches in the chat (videos, photos) arrive under
`/root/.claude/uploads/<session>/`: copy them into `Raw/<name>/` (or `Reference/<name>/`)
with sensible names. Or the owner pastes links:
- Footage/music: usually a Google Drive file or folder link →
  `python3 tools/fetch.py "<link>" --project <name> --to raw`
- Inspiration: Instagram/TikTok/Facebook link, or a Drive link to a screen recording →
  `python3 tools/fetch.py "<link>" --project <name> --to reference` (also analyses it)

If a Drive link fails, ask them to set sharing to "Anyone with the link". YouTube
blocks cloud downloads: ask them to screen-record the YouTube video (Control Centre ⏺)
and share it via Drive. Instagram/TikTok can also fail for private posts: same fix.
Screen recordings contain the phone's status bar: ignore it when studying the style.

**3. Study the inspiration.** For each reference: read `analysis.md`, LOOK at
`sheet.jpg` and several `shot_###.jpg` frames, and transcribe it if it has speech.
Note: pacing (shot length), hook in the first 2 s, framing, caption style (font feel,
size, position, colour, words per line, highlight, animation), titles, stickers/emoji,
motion (zooms, punch-ins, shakes), transitions, colour/look, music, ending.

**4. Remember the style.** If the owner says this inspiration is for future videos
too (or it's the first one), save it: `python3 tools/save_style.py <style-name>
--project <name> --reference <file> --default`, then edit `styles/<style-name>/style.json`
and `style.md` to match what you saw (fonts from fonts/README.md). Commit and push the
style so future sessions have it. Without a new inspiration, use the default style
(`styles/default.txt`) and say which style you used.

**5. Study the footage.** `python3 tools/analyze.py "<clip>" --project <name>` for every
raw clip (look at the frames), and `python3 tools/transcribe.py <clips...> --project <name>
--language ur` for clips with speech. Use the transcripts to pick the best lines and cut
mistakes, pauses and repeats.

**6. Write the edit.** Create `Export/<name>/edit.json` (see `tools/EDIT_FORMAT.md`).
Fill `summary`, `reference_notes` and a `description` for every shot. Use motion
graphics the way the style does: `motion`, `punch`, `shake` on shots; `texts` with
animations and `lower_third`; `overlays` with emoji/stickers; `progress_bar`.

Product photos: `python3 tools/cutout.py "<image>"` makes a clean transparent cutout
(BiRefNet). Always look at the cutout on a dark and a bright background before using it.
Show it when the product is mentioned (`overlays`, not too big, never over a face), and
use a `backdrop` (blur + dim) behind a big product card at the end.

Icon badges for features/ingredients said in the video (vitamins, minerals, DCP ...):
`python3 tools/badge.py --project <name> --label VITAMINS --emoji 💊 --color "#8E44AD"`;
pop them up (upper part of the frame, ~22% width) exactly when the word is spoken.

**Owner's standing preferences** (see styles/bold-clean/style.md): keep the video CLEAN,
no clutter; captions must be attractive (bold trending fonts: Poppins, Anton), never basic;
good SFX. Extra effects such as the liquid glass cards (`"glass"`, styles/liquid-glass/)
only when the owner asks for them by name.

Sound effects: `"sfx"` in edit.json with the built-in synthesised sounds (`tools/sfx.py`:
whoosh, whoosh_fast, swoosh_up, pop, click, ding, ching, impact, boom, riser, glitch) or
the owner's own files. Typical reel use: impact on the hook, whoosh on cuts/titles, pop
when a sticker/cutout appears, ding/ching on key facts. Keep them under the voice (0.3–0.6).

Captions: `python3 tools/captions.py "<edit.json>"`, then
`python3 tools/caption_text.py export "<edit.json>"`, rewrite `captions.txt`, then
`python3 tools/caption_text.py apply "<edit.json>"` (keep the same total number of words
and you can re-break lines freely with exact word timing, e.g. keep a brand name on one line).
Whisper writes Urdu speech in Urdu script. The owner wants **Roman Urdu** captions by
default: rewrite every line in natural Roman Urdu (yeh, hai, nahi, kya, mein, aap,
bohat, acha, kaise, kyun), keeping word-for-word order where possible so the word
highlighting stays in sync, and fix names and recognition mistakes. Never invent
words that weren't said; if a part is unclear, mark it and ask.

**6b. Caption check (ALWAYS, before any final render).** The owner checks captions on
the Caption Review page (https://claude.ai/artifact/WNJDd3kh3petc3Hgc3cXY5): one editable
line per caption, Enter saves. `python3 tools/caption_review.py push "<edit.json>" --note
N="..."` writes `work/review/batch.json`; send it with ArtifactData `batch` (existing docs
need `if_version`: read them first). Mark unclear words with `_` and a note in Urdu. Send the
owner the link. When they say OK: ArtifactData `list` of `projects/<name>/lines` with
`out_dir` `Export/<name>/work/review/pulled`, then `python3 tools/caption_review.py pull
"<edit.json>" "<that dir>"`.

**Product palette.** When the owner gives a product (and its cutout), take the accent
colours from the product's own packaging and use them for captions, titles and badges (e.g.
Heavy Gold: gold #FFD400 + royal blue #1E3FA0 + white). Motion graphics for products: cutout
rises in when the product is named with a title above it ("HEAVY GOLD / 5 in 1"), icon
badges for each feature as it is spoken, product card at the end.

**Quality.** Never lose quality: keep the source resolution, final renders use CRF 17 /
preset slow (style `quality`), check a full-resolution frame before delivering. A subtle
cinematic touch (warmth, light grain, vignette) but nothing that smears detail.

**7. Storyboard → approval.** `python3 tools/storyboard.py "<edit.json>"`. Look at
`storyboard/overview.jpg` yourself first and fix problems (bad framing, text off-screen,
unreadable captions, stickers covering faces). Then send `storyboard/overview.jpg` with
SendUserFile and a short Urdu summary listing the shots by number (what happens, text,
effects, music). **STOP and wait for OK.** Never render the final video before approval.
For changes, edit and send a new storyboard.

**8. Render and deliver.** After approval: `python3 tools/render.py "<edit.json>" --preview`,
check a few frames of it, then `python3 tools/render.py "<edit.json>"`. Send
`Export/<name>/<name>.mp4` with SendUserFile and tell them: open it → Share → Save Video.
If it is too large to send, re-render with `"quality": {"crf": 23}`. Commit and push
edit.json, captions.json, storyboard.md and storyboard images (never media files).

## Rules
- Never change or delete files in `Raw/` or `Reference/` except `brief.md`.
- Reference videos are for studying style only: never put their footage or music in
  the owner's video.
- If a font is missing, download it: `python3 tools/get_fonts.py "Family:400,700" --folder "<category> Fonts"`
  and commit it. Do not silently fall back.
- Motion graphics are limited to what the tools do (see EDIT_FORMAT.md). If the owner
  wants something they can't do (3D, tracking, complex animation), say so plainly and
  offer the closest thing.
