---
name: owais-voice
description: Write hooks, voice-over lines, on-screen text and post captions in the owner's own voice (Owais, livestock-feed shop at Denso Hall, Karachi - Heavy Gold, Mega-VMix, Buttery Milk, Hepta Sef...). Use for any script, hook, caption, status line, TikTok/Facebook post text or reel idea for the owner's business videos, so it sounds like him and not like AI.
---

# Owais voice: dispatch-reel Urdu

Learned 2026-11-19 from the owner's best posts: the viral Buttery Milk "Anda More" reel, Heavy Gold
"Liaquatabad / Ali bhai" (repeat purchase) and Heavy Gold "Naveed bhai, rooftop goat farmer", plus his
Khanpur, Quetta and Rawalpindi dispatch videos. Full texts: `examples.md`.

## Who is talking
A shopkeeper filming real dispatches on his phone, talking to people who already know livestock.
Warm, proud of his customers, quick, a bit street. Never sounds like an ad agency. He never explains
what a cow is or why feed matters: the audience already knows.

## The shape of almost every reel (10-15 s spoken)
1. **PLACE first** (the hook): a known area / city + a little pride.
   "Liaquatabad, Karachi ka mashhoor ilaqa." · "Anda Mor ka ilaqa hai Karachi mein." · "Khanpur ki taraf…"
2. **WHO + WHAT goes**: customer with a respectful nickname + a descriptor, quantity, product.
   "Wahan par Ali bhai ko do bag ja rahe hain, bhai, Heavy Gold ke." ·
   "Rooftop par zabardast bakre paalne wale Naveed bhai, Heavy Gold ke bag liye unhon ne."
3. **ONE benefit, in plain words**, as the bag/customer says it (no claims beyond that).
   "Minerals, vitamins ka zabardast powder hai, bhai." · "Protein aur butter fat wala doodh hai bhai."
4. **PROOF**: repeat purchase, long-time use, customer's own words, trust from far cities.
   "Repeat purchase pe ja raha hai, bhai, ye." · "Bade arse se chala raha hoon…" (customer) ·
   "Log bada trust karte hain." · "Quetta se hain."
5. **PUNCH LINE that ends it** (short, loops back): "Acchi product ki asal pehchan hi yahi hoti hai." ·
   "Brand hai brand, waqai." · "Result hai na." · "Quality hai na bhai."

## Word habits (use them, lightly)
- "bhai" as rhythm (1-3 times per reel), "sahab" for elders/far customers, "hamare X bhai".
- zabardast, top-notch, mashhoor, waqai, bade shauqeen, result, quality, trust, repeat purchase.
- Numbers and units: "do bag", "minimum aath pouch", "25 kg", "chaar din pehle".
- Mix of Urdu + common English trade words (repeat purchase, feedback, quality, brand, dispatch).
- Roman Urdu spelling: yeh/ye, hai, hain, bhi, ke, ka, ki, mein, wahan, unhon ne, jaate jaate.

## Never
- AI tells: "it's not X, it's Y", "no X, no Y, no Z", "unlock", "elevate", "game-changer",
  "journey", em dashes, three-adjective lists, rhetorical "Imagine…" openers.
- Medical / guaranteed results (weight gain in N days, cures). Only what the bag or the customer says.
- Inventing names, cities, quantities, prices or phone numbers.
- Long sentences: one breath per line, max ~10 words.

## Hooks (first 2 s), ranked by what worked
1. Area/city name + "ka mashhoor ilaqa" / "ki taraf" (viral pattern).
2. Customer + vivid descriptor ("rooftop par zabardast bakre paalne wale…").
3. Proof-first ("Repeat purchase pe ja raha hai ye…", "Chaar din pehle paise de gaye, aaj maal lene aaye").
4. Benefit as 2 words on screen ("WAZAN *Tez*", "ANDA *More*") with the spoken line under it.
Check each hook with `.claude/skills/ig-reel/hookscore.py` (English-biased) AND by hand: specific
(place/name/number)? stakes or pride? payload word early? talks to the viewer? short?

## Post captions (TikTok + Facebook, one copy-paste block)
Line 1 = place + what went ("Liaquatabad, Karachi se phir order aaya 🔁✅"); line 2 = customer + product;
line 3 = proof/punch line; then the product with ✔️ features from the bag; a question to the viewer
("Aap ka area konsa hai?"); "order ke liye inbox karein 📩"; keywords line; 10-15 hashtags
(#HeavyGold #<Area> #Karachi #DensoHall #CattleFeed …). Emojis: 3-6, never a wall of them.
Run the text through `ig-human` before showing it.

## On-screen design that goes with this voice
Raw real footage, area name typed big in frame 1, captions only (plain-captions / clean styles),
optional bottom strip with customer photo + name + descriptor + product (as in the Naveed reel).
