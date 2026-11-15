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

**Creative standard:** read `guides/creative-director.md` before designing anything: think,
plan, create and critique like an elite international creative agency (authenticity,
typography, composition, real photography and storytelling over decoration and templates).

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
