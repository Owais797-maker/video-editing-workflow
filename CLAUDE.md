# Video editing workflow

This repo is used to edit videos with Claude. The owner gives raw footage, one or
more reference ("inspiration") videos and instructions; Claude makes a storyboard,
waits for approval, then renders the video with FFmpeg through the scripts in `tools/`.

The owner writes in Urdu (sometimes English). Reply in the language they used.
Keep replies short and non-technical; they are a video creator, not a programmer.

## Folders

```
Video Edits/Raw/<project>/         footage + music (never modify or delete these files)
Video Edits/Reference/<project>/   inspiration videos + brief.md (the instructions)
Video Edits/Export/<project>/      edit.json, captions.json, storyboard.md, storyboard/, final video
Video Edits/Export/<project>/work/ analysis, transcripts, render scratch (git-ignored)
fonts/                             .ttf/.otf fonts (searched recursively); see fonts/README.md
tools/                             scripts; tools/EDIT_FORMAT.md documents edit.json
```

Video and audio files are git-ignored (too big for GitHub). Do not commit them.

## The workflow — follow these stages in order

**0. Setup.** On a new machine run `setup/setup-windows.ps1` (PowerShell, with
`-ExecutionPolicy Bypass`) or `bash setup/setup-mac.sh`, installing Git first if needed.
If something fails later: `python tools/check_setup.py`. On a Mac the scripts use a
virtualenv: run every tool with `.venv/bin/python` instead of `python`.

**1. Start.** `python tools/new_project.py <name>` if the folders don't exist. Read
`Reference/<name>/brief.md` and anything the owner said. If key facts are missing
(platform/size, length, captions yes/no + language), ask in ONE short message.

**2. Study the reference.** If the owner sends a link (YouTube, Instagram, TikTok,
Facebook...), download it first: `python tools/fetch_reference.py "<url>" --project <name>`
(it also runs analyze.py). If it fails because a login is needed, retry with
`--cookies-from chrome` (or edge/firefox/safari, whichever browser they use) and tell
them. Reference videos are for studying style only: never put their footage or music
in the owner's video. For each reference video:
`python tools/analyze.py "<path>" --project <name>`, then read its `analysis.md`
and LOOK at `sheet.jpg` and several `shot_###.jpg` frames. Note: shot length and
pacing, framing (close-ups, crops), caption style (font feel, size, position, colour,
words per line, highlight), on-screen titles, transitions, colour/look, hook in the
first 2 seconds, ending. If the reference has speech, transcribing it helps too.

**3. Study the raw footage.** Run `analyze.py` on every raw clip (look at the frames
to know what is in each clip and where), and `python tools/transcribe.py <clips...>
--project <name> --language <ur|en|...>` for clips with speech (model `medium` or
better for Urdu). Use the transcripts to choose the best lines and cut out
mistakes, pauses and repeats.

**4. Write the edit.** Create `Export/<name>/edit.json` (see `tools/EDIT_FORMAT.md`)
matching the reference style and the brief. Fill `summary`, `reference_notes`
and a `description` for every shot. If captions are wanted:
`python tools/captions.py "<edit.json>"`, then
`python tools/caption_text.py export "<edit.json>"`, edit `captions.txt` (fix
transcription errors, names) and `python tools/caption_text.py apply "<edit.json>"`.

**Caption language.** Whisper writes Urdu speech in Urdu script. For **Roman Urdu**
(e.g. "yeh mera pehla vlog hai") or English captions, transcribe with
`--language ur`, export `captions.txt`, and rewrite every line yourself in Roman Urdu
(common spellings: yeh, hai, nahi, kya, mein, aap, bohat, acha) or English, keeping
word-for-word order where possible so the word highlighting stays in sync. Then
`apply`. Use a Latin font (Poppins ExtraBold, Montserrat ExtraBold, Bebas Neue…) for
Roman Urdu/English and an Urdu font for Urdu script.

**5. Storyboard → approval.** `python tools/storyboard.py "<edit.json>"`. Look at
`storyboard/overview.jpg` yourself first and fix anything wrong (bad framing, text
off-screen, unreadable captions). Then show the owner: send `storyboard/overview.jpg`
and `storyboard.md` (SendUserFile when available, otherwise give the paths), with a
short summary of the plan. **STOP and wait.** Never render the final video before the
owner says OK. For change requests, edit `edit.json`/`captions.json`, regenerate the
storyboard and ask again.

**6. Render.** After approval: `python tools/render.py "<edit.json>" --preview` and check a
few frames of it (`ffmpeg -ss <t> -i <file> -frames:v 1 frame.jpg`), then
`python tools/render.py "<edit.json>"`. Give the owner the path of
`Export/<name>/<name>.mp4` (and send it if possible). Further changes go back to step 4/5
only if they change the story; small fixes (text size, music volume) can be re-rendered
directly with a preview first.

## Rules
- Never change or delete anything in `Raw/` or `Reference/` except `brief.md`.
- Never invent transcript text; if Whisper is unsure, mark it and ask.
- If a font the style needs is missing from `fonts/`, download it from Google Fonts:
  `python tools/get_fonts.py "Family Name:400,700" --folder "<category> Fonts"`, and
  commit it (fonts are small and Open Font License). Do not silently fall back.
- Commit edit.json, captions.json, storyboard.md and storyboard images (small text/images)
  so the project history is kept; never commit media files.
