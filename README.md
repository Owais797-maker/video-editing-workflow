# video-editing-workflow

Video editing projects, creative assets, editing templates, automation scripts and production workflows.

Claude edits videos here with FFmpeg: you give footage, an inspiration video and instructions → Claude makes a **storyboard** → you approve → Claude renders the **final video**.

---

## ایک بار کا سیٹ اپ (اپنے کمپیوٹر پر)

ویڈیو فائلیں بڑی ہوتی ہیں، اس لیے یہ کام **اپنے کمپیوٹر پر Claude Code** کے ساتھ بہترین چلتا ہے۔

### 1. یہ چیزیں انسٹال کریں

| چیز | کس لیے | Windows | Mac |
|---|---|---|---|
| Claude (desktop app) | Claude Code چلانے کے لیے | claude.ai/download | claude.ai/download |
| Git | ریپو ڈاؤن لوڈ کرنے کے لیے | `winget install Git.Git` | `xcode-select --install` |
| Python 3.9+ | اسکرپٹس اور Whisper | `winget install Python.Python.3.12` | `brew install python` |
| FFmpeg | ویڈیو ایڈٹنگ کا انجن | `winget install Gyan.FFmpeg` | `brew install ffmpeg` |

Windows پر کمانڈز **PowerShell** میں چلائیں۔ Mac پر پہلے [Homebrew](https://brew.sh) انسٹال کریں۔ انسٹال کے بعد ٹرمینل بند کر کے دوبارہ کھولیں۔

### 2. ریپو ڈاؤن لوڈ کریں اور Whisper انسٹال کریں

```
git clone https://github.com/Owais797-maker/video-editing-workflow.git
cd video-editing-workflow
pip install -r requirements.txt
```

Whisper (آواز سے کیپشن) کا ماڈل پہلی بار استعمال پر خود ڈاؤن لوڈ ہوگا۔ اردو کے لیے `medium` ماڈل تقریباً 1.5GB کا ہے، ایک ہی بار ڈاؤن لوڈ ہوتا ہے۔

### 3. فونٹس

21 مفت فونٹس (اردو نستعلیق، کیپشن، ٹائٹل، سنیمیٹک) پہلے سے `fonts/` میں موجود ہیں، اور ریپو کے ساتھ خود آ جاتے ہیں۔ فہرست `fonts/README.md` میں ہے۔ اور فونٹ چاہیے تو Claude سے کہیں، یا خود چلائیں:

```
python tools/get_fonts.py "Lobster"
```

### 4. چیک کریں

```
python tools/check_setup.py
```

سب `[OK]` آئے تو سیٹ اپ مکمل ہے۔

---

## ہر ویڈیو کے لیے طریقہ

1. Claude app میں **Code** کھولیں اور یہ ریپو کا فولڈر چنیں۔
2. Claude سے کہیں: **"نیا پروجیکٹ بناؤ: eid-reel"**۔ یہ تین فولڈر اور ایک `brief.md` بنا دے گا۔
3. فائلیں رکھیں:
   - `Video Edits/Raw/eid-reel/` میں اپنی فوٹیج اور میوزک
   - `Video Edits/Reference/eid-reel/` میں انسپریشن ویڈیو
4. `brief.md` بھریں، یا Claude کو چیٹ میں بتا دیں کہ کیسی ایڈٹنگ چاہیے۔
5. Claude ریفرنس اور فوٹیج دیکھ کر **اسٹوری بورڈ** دکھائے گا: ہر شاٹ کی تصویر، وقت، ٹیکسٹ اور کیپشن۔
6. **OK** لکھیں، یا تبدیلیاں بتائیں (مثلاً "شاٹ 3 چھوٹا کرو، کیپشن بڑے کرو")۔
7. Claude فائنل ویڈیو `Video Edits/Export/eid-reel/eid-reel.mp4` میں بنا دے گا۔

ویڈیو اور آڈیو فائلیں GitHub پر نہیں جاتیں (`.gitignore`)، صرف آپ کے کمپیوٹر پر رہتی ہیں۔ GitHub پر صرف ہدایات، اسٹوری بورڈ اور ایڈٹ کی فائلیں محفوظ ہوتی ہیں۔

---

## Tools

| Script | What it does |
|---|---|
| `tools/check_setup.py` | Checks FFmpeg, Whisper and fonts |
| `tools/get_fonts.py [family]` | Downloads free Google Fonts into `fonts/` |
| `tools/new_project.py <name>` | Creates the project folders and `brief.md` |
| `tools/analyze.py <video> --project <name>` | Cuts, shot lengths, loudness, frames + contact sheet |
| `tools/transcribe.py <clips> --project <name>` | Whisper speech-to-text with word timings |
| `tools/captions.py <edit.json>` | Captions on the final timeline (editable `captions.json`) |
| `tools/caption_text.py export/apply <edit.json>` | Caption wording as plain text: fix it or rewrite in Roman Urdu/English, timings kept |
| `tools/storyboard.py <edit.json>` | Storyboard (`storyboard.md` + framed frames with text) |
| `tools/render.py <edit.json> [--preview]` | Final video |

The edit is described in `edit.json`; see [tools/EDIT_FORMAT.md](tools/EDIT_FORMAT.md). Workflow rules for Claude are in [CLAUDE.md](CLAUDE.md).
