# Styles (انداز کی یادداشت)

Each folder here is an editing style learned from an inspiration video. Every new
video uses the **default style** (named in `default.txt`) unless the owner asks for
another one or for something different. The reference videos themselves are not
stored, only what was learned from them.

```
styles/<name>/style.json   defaults merged into every edit.json that uses the style
styles/<name>/style.md     the style in words: pacing, hook, captions, titles, look, music
styles/<name>/sheet.jpg    contact sheet of the reference video
styles/<name>/pacing.json  measured shot lengths of the reference
styles/default.txt         name of the default style
```

How a style is applied (`tools/edl.py`): `edit.json` values always win. From the
style come `output`, `look`, `fade`, `loudness`, `progress_bar`, the caption style
(when the edit has `"captions"`), music volume/ducking (when the edit has music),
the default `transition` and `motion` for shots that don't set one, and defaults for
`text`, `lower_third` and `overlay` items. Set `"style": null` in an edit to use none,
or `"style": "<name>"` to pick a specific one.

Create one with `python tools/save_style.py <name> --project <p> --reference <video> [--default]`,
then fill in `style.json` and `style.md` from what you saw in the reference.
