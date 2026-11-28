# Product posts — LOCKED (owner, 2026-11-21: "yeh mizaaj bara pasand aa raha hai, isko lock karo")

Static 9:16 posts (2160×3840, 4K) for each product, for WhatsApp status / FB / IG and for **resellers**.
Make every new product post, price list or DP in THIS look unless the owner asks for something else.

**Make one:** copy a json in `tools/posts/` (closest product), change texts/colours/src, then
`python3 tools/posts/product_post.py tools/posts/<product>.json` → `Video Edits/Export/<name>/<name>.jpg`.
Look at the full image, fix anything touching the edges or covering bag text, commit, send.

## The look
- Clean white/light-grey studio background (soft radial light + faint diagonal sheen). Lots of air.
- Top: tiny tracked label `PRODUCT NAME · TYPE` (Montserrat, product name bold, half in the accent colour).
- Line 1: **Jameel Noori Nastaleeq** sentence, one key word in **Aslam** + accent colour.
- Hero: big **Aslam** Urdu line in the product's own colour (gradient light→dark, soft coloured shadow).
  Keep ~6% side margin: if it touches the edges, lower `hero_size` (130–170). Words that join (پاؤر وی) get
  inline-block spans with a gap.
- Product name in English: **Montserrat Black** caps, second word in the accent colour.
- Product cutout on a white disc with a soft floor shadow, 2× / 3× upscaled + sharpened.
- Two filled badges (pills with a ✓ circle, small caps line + big line in **Poppins**): one in the product
  colour, one in the bag's second colour; slightly tilted; anchored on BLANK parts of the bag (top/zip area,
  white base, sky) — never over the logo, name or ingredient circles.
- Bottom: **Poppins** English line (accent words coloured) + Noori Urdu line (key word Aslam) + tiny tracked footer.
- Colours from the packaging: Heavy Gold royal blue+gold, Buttery Milk red+green, Hepta Sef purple+yellow,
  Mega-VMix blue+red, Power V-Mix navy+gold, Mega-Tox orange+navy, Gripe Water blue+navy.

## Rules
- **No shop name, no phone number, no QR** (resellers use them) unless the owner asks. Power V-Mix bag:
  use `power-vimix-reseller-cutout.png` (logo, number and QR removed).
- Only claims printed on the bag or said by the owner; no disease/cure claims (mastitis etc.).
- Owner's spelling of product names: "پاؤر" with hamza, Power VIMIX, Mega-VMix, Mega-Tox Plus, Buttery Milk.

## Same family
- Price list (`Export/price-list/`): "پرائس لسٹ" Aslam red + PRICE LIST; numbered white cards with product
  thumbnail, name (Montserrat Black), size line, price in red Poppins; small TURKEY tag on Mega-Tox / Mega-VMix.
- WhatsApp DPs (`Export/whatsapp-dp/`, `Export/dp-muddassir/`): red ring badge, red/white, name big red
  Poppins, red pill, line-art cow + goat drawn from the owner's own photos (owner wants sketches, never photos).

## Owner 2026-11-27: less Aslam
Aslam is too heavy when used everywhere ("bohat mota, samajh nahi aata"). Use Jameel Noori Nastaleeq for Urdu lines and Mehr Nastaliq for the big Urdu hook line; Aslam only for a single short accent word, if at all. Example: tools/posts/calsol_post.py.

## Owner 2026-11-28 (videos too): Urdu lines in Noori; Aslam ONLY for the one key word/phrase of a line (other highlights = colour only). Hook plates the same.
