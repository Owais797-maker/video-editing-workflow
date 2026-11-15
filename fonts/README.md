# Fonts

Free Google Fonts (Open Font License: free for commercial videos), downloaded with
`python tools/get_fonts.py`. Add more with
`python tools/get_fonts.py "Family Name:400,700" --folder "Bold Display Fonts"`.

In `edit.json`, use the **font name** (left column), not the file name.

| Font name | Folder | Good for |
|---|---|---|
| Noto Nastaliq Urdu | Urdu Fonts | Urdu titles in classic Nastaliq (use a bigger `size`, about 1.5x) |
| Gulzar | Urdu Fonts | Decorative Nastaliq titles |
| Noto Naskh Arabic | Urdu Fonts | Clear Urdu captions (Naskh style, easier to read fast) |
| Poppins, Poppins SemiBold, Poppins ExtraBold | Subtitle Fonts | Roman Urdu / English captions (reels style) |
| Montserrat (500 Medium, 800 ExtraBold) | Subtitle Fonts | Captions and clean titles |
| Roboto | Subtitle Fonts | Plain subtitles for long videos |
| Bebas Neue, Anton, Archivo Black | Bold Display Fonts | Big hook text and titles |
| Luckiest Guy, Bangers | Social Media Fonts | Fun / comic captions |
| Cinzel, Playfair Display | Cinematic Fonts | Cinematic, wedding, luxury titles |

For Poppins SemiBold / ExtraBold set `"bold": false` (the weight is already in the font).

## Guidelines

- Use licensed fonts only (all fonts here are Open Font License).
- Maintain consistent typography: one font for captions, at most one more for titles.
- Keep text readable on mobile screens.
