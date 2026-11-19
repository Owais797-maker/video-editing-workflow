# Urdu typography skill (TikTok hooks in Urdu script)

Why: the owner's biggest TikTok hits (205k, 114k, 102k…) all open with a BIG URDU-SCRIPT line that names a
farmer's pain or want + the solution ("منہ کھر کی زبردست ویکسین", "جانوروں کا وزن تیزی سے بڑھانے والا…").
Farmers read Urdu first. Use this for every TikTok hook (Facebook too when it fits).

Tool: `python3 tools/urdu_text.py --project P --name hook --line "text:preset[:scale]" … [--plate dark|black|red|blue|yellow|#hex]`
→ `Video Edits/Raw/P/urdu-hook.png`, drawn at 2x (sharp in 4K). Put it in `overlays` on frame 1,
fully visible at 0.0 s (animation "none" or a 0.1 s pop), upper third, width 0.8–0.9, never over a face.
Preview of the styles: guides/urdu-styles.jpg.

## Fonts (all free, Urdu-complete: ٹ ڈ ڑ ں ھ ے ۓ)
| Preset | Font | Use |
|---|---|---|
| nastaliq / nastaliq-gold / nastaliq-red | Gulzar (Noori-Nastaleeq style) | the classic Urdu look: question / pain line |
| bold / bold-yellow / bold-red | Lalezar (heavy poster) | the punch: product, benefit, "زبردست …" |
| ruqaa | Aref Ruqaa (calligraphy) | ONE elegant word (صحت، برکت) |
| naskh | Noto Naskh Arabic Bold | small, very readable lines |
| kufi | Reem Kufi | short words only (its ے looks odd in long text) |
| latin | Montserrat Black | English product name inside an Urdu stack (BUTTER FAT MILK) |
Also installed: Noto Nastaliq Urdu (400/700), Mirza, Lateef, Markazi Text, Vazirmatn (Persian, check Urdu letters).
Jameel Noori Nastaleeq itself is not on Google Fonts (licence unclear): Gulzar is the free look-alike.

## Recipes that match the hits
1. **Pain → product** (2 lines): `"جانور کا وزن نہیں بڑھ رہا؟:nastaliq"` + `"ہیوی گولڈ:bold-yellow:1.3"`, `--plate dark`.
2. **Season + promise**: `"قربانی کے مال کے لیے:nastaliq-gold"` + `"زبردست امپورٹڈ:bold:1.2"`, `--plate black`.
3. **Who it's for + name + benefit** (3 lines, no plate on dark footage): naskh + latin + bold-red.
4. **Poster (red plate)**: `"منہ کھر کی:nastaliq:1.1"` + `"زبردست ویکسین:bold:1.3"`, `--plate red`.
Rules: max 2–3 lines, ≤ 5 words per line, one colour accent, Nastaliq for the "voice" line and Lalezar for the
punch; use a plate whenever the background is busy (packaging, shop shelves). Only claims the bag/customer makes.
