# video-editing-workflow

Video editing projects, creative assets, editing templates, automation scripts and production workflows.

Claude edits videos here with FFmpeg, entirely in a Claude Code cloud session driven from an iPhone: you give footage + an inspiration video + instructions → Claude makes a **storyboard** → you approve → Claude sends the **final video** back in the chat.

---

## iPhone سے ویڈیو ایڈٹ کروانے کا طریقہ

### ایک بار کی تیاری
1. App Store سے **Claude** اور **Google Drive** انسٹال کریں۔
2. Claude app میں **Code** کھولیں اور یہ ریپو (`video-editing-workflow`) اور environment **video-editing-workflow** چنیں۔ اس environment میں انٹرنیٹ کھلا ہے اور سب ٹولز خود انسٹال ہوتے ہیں۔

### ہر ویڈیو کے لیے
1. **فوٹیج:** اپنی ویڈیوز اور میوزک Google Drive کے ایک فولڈر میں اپلوڈ کریں۔ فولڈر پر **Share → General access → Anyone with the link** کریں، پھر **Copy link**۔
2. **انسپریشن:** Instagram، TikTok یا Facebook ویڈیو کا لنک کاپی کریں۔ YouTube کی ویڈیو ہو تو اسے **Screen Recording** سے ریکارڈ کر کے Drive میں ڈال دیں (YouTube cloud سے ڈاؤن لوڈ نہیں ہونے دیتا)۔
3. **Claude کو لکھیں**، مثلاً:
   > نیا پروجیکٹ: eid-reel۔ فوٹیج: (Drive لنک)۔ انسپریشن: (Instagram لنک)۔ 30 سیکنڈ کی reel بناؤ، رومن اردو کیپشن، تیز کٹنگ، آخر میں "Follow karein"۔ یہ انداز آئندہ کے لیے بھی یاد رکھو۔
4. Claude **اسٹوری بورڈ** کی تصویر بھیجے گا۔ **OK** لکھیں، یا تبدیلی بتائیں (مثلاً "شاٹ 3 چھوٹا کرو")۔
5. Claude **فائنل ویڈیو** چیٹ میں بھیجے گا۔ اسے کھولیں → **Share → Save Video**۔

> cloud سیشن ختم ہونے پر اس کی ویڈیو فائلیں مٹ جاتی ہیں۔ اصل فوٹیج Drive میں اور فائنل ویڈیو Photos میں رکھیں۔ انداز (styles)، اسٹوری بورڈ اور ایڈٹ کی فائلیں GitHub پر محفوظ رہتی ہیں۔

### Claude کیا کر سکتا ہے
- کاٹنا، ترتیب، رفتار، 9:16 / 16:9 / 1:1، رنگ، میوزک (بولنے پر خود دھیما)، آواز کی سطح
- رومن اردو، اردو یا انگریزی کیپشن، بولا جانے والا لفظ رنگ اور سائز سے نمایاں
- موشن گرافکس: آہستہ zoom اور pan، زور والے لفظ پر punch-in zoom، shake، ٹائٹل کی pop / slide / typewriter animation، نام کی پٹی (lower third)، چلتے ہوئے emoji اور اسٹیکر، progress bar، ٹرانزیشنز
- انسپریشن کا انداز `styles/` میں یاد رکھنا اور آئندہ ہر ویڈیو میں استعمال کرنا

After Effects جیسا کام (3D، tracking، پیچیدہ animation) نہیں ہو سکتا۔

---

## Tools

| Script | What it does |
|---|---|
| `tools/check_setup.py` | Checks FFmpeg, Whisper, yt-dlp, gdown and fonts |
| `tools/new_project.py <name>` | Creates the project folders and `brief.md` |
| `tools/fetch.py <links> --project <p> --to raw\|reference` | Downloads from Google Drive (files/folders), Dropbox, direct links, Instagram/TikTok/Facebook |
| `tools/analyze.py <video> --project <p>` | Cuts, shot lengths, loudness, frames + contact sheet |
| `tools/save_style.py <name> --project <p> --reference <video>` | Saves a reference's editing style to `styles/` |
| `tools/transcribe.py <clips> --project <p>` | Whisper speech-to-text with word timings |
| `tools/captions.py <edit.json>` | Captions on the final timeline (`captions.json`) |
| `tools/caption_text.py export/apply <edit.json>` | Caption wording as plain text: fix it or rewrite in Roman Urdu, timings kept |
| `tools/storyboard.py <edit.json>` | Storyboard frames from a quick preview render |
| `tools/render.py <edit.json> [--preview]` | Final video |
| `tools/get_fonts.py [family]` | Downloads free Google Fonts into `fonts/` |

The edit is described in `edit.json`; see [tools/EDIT_FORMAT.md](tools/EDIT_FORMAT.md). Workflow rules for Claude are in [CLAUDE.md](CLAUDE.md). Styles: [styles/README.md](styles/README.md).

The `setup/` scripts install everything on a Windows or Mac computer, if one is ever used.
