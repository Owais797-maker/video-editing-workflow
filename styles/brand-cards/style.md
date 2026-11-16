# Style: brand-cards (motion-graphics product reel, on request or for product reels)

Learned from a Facebook reel for "Buttery Milk" (Khyber Traders / AnimalHealth.PK), shared by
the owner on 2026-11-16: "keep this style: green screen cards with the bag coming in".

![reference](sheet.jpg)

## The look
- **Framed footage:** the talking video sits inside a rounded card with a thick accent
  (yellow) border on the brand background; logo badge at the top centre.
- **Brand cards between moments** (voice keeps playing): full-frame brand-colour radial
  gradient (green there) with soft drifting bokeh circles and a thin accent progress line
  at the top. Small accent **label pill** ("BUTTERY MILK", "CUSTOMER REVIEW"), big two-tone
  **Oswald headline** (white + accent: "TRUSTED / FOR YEARS", "TOP-LEVEL QUALITY", "ASKED FOR
  BY NAME", "VIP RESULTS", "HAPPY FARMER!"), the **product cutout** popping in and floating.
- **Stats card:** left-aligned big accent numbers with black tags ("26–28% BUTTER FAT",
  "34% PROTEIN"), small product bottom-right.
- **End card:** logo, brand line, accent pill with phone numbers, handle.
- Captions small, white, clean (sentence case) at the lower third; name strip in accent
  caps ("GHULAM RASOOL / GOAT FARM").

## How to build it here
`"frame"` + `"brand"` + `"cards"` in edit.json (tools/cards.py, see tools/EDIT_FORMAT.md).
Brand colours come from the product (Buttery Milk: green #1E8C3A/#0A3A17 + yellow #F5C518;
Heavy Gold: royal blue #2453C8/#0B1E57 + gold #FFD400). Only real product facts on stats
cards (from the packaging or the owner), never invented numbers or claims.
