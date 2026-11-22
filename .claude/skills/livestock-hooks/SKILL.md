---
name: livestock-hooks
description: >-
  Write scroll-stopping hooks (first 2 seconds: on-screen Urdu heading + spoken line) for the owner's
  livestock-feed / vet-store videos and posts (Khyber Traders: Heavy Gold, Mega-VMix, Power V-Mix, Buttery
  Milk, Lacto Sol, Hepta Sef, Gripe Water, Mega-Tox, Milkolin, Ratawa…; customers, dispatches, Qurbani
  animals, dairy farms). Use whenever the owner asks for a hook, heading, title, thumbnail line, "3 heading
  options", or "viral" text for TikTok / Instagram / Facebook / WhatsApp status in his field.
---

# Livestock hooks (owner's niche)

Built on: `ig-reel` (26 hook formulas + `hookscore.py`), `owais-voice` (his own words), and his real data
(`guides/viral-breakdown.md` → Learned patterns). Read those when you need more depth.

## What his data proves (TikTok @ktvet1, 1,298 posts)
- Hits (205k, 114k, 102k, 90k…) all had a **big Urdu-script hook on frame 1** naming a farmer's **pain or
  want + the solution**, e.g. "جانوروں کا وزن تیزی سے بڑھانے والا Butter Fat Milk", "منہ کھر کی زبردست ویکسین".
- **Qurbani season** (Jan–May) multiplies everything. Animals in frame beat motion graphics.
- Hook fully visible at 0.0 s (no typing-in), clearest shot first, 8–18 s videos, hashtags-only on TikTok.
- Flops: Roman/English design text, blurry first second, generic "Last night event", long sales captions.

## Hook formulas for his field (pick 3–5 different ones every time)
| # | Formula | Example (on-screen Urdu) |
|---|---|---|
| 1 | **Pain question** | جانور کا وزن نہیں بڑھ رہا؟ |
| 2 | **Benefit + product** | قربانی کے جانوروں کا وزن بڑھانے والا زبردست پاؤڈر |
| 3 | **Number / result** | 1 کلو پاؤڈر سے 10 لیٹر دودھ |
| 4 | **Place + journey** (dispatch) | کراچی سے خانپور تک ہیوی گولڈ 🚚 |
| 5 | **Customer proof** | 4 دن پہلے پیسے دیے، آج مال لینے کوئٹہ سے آئے |
| 6 | **Repeat buyer** | تیسری بار لینے آئے… رزلٹ ہے نا! |
| 7 | **Kid / surprise** | بچے نے حیران کر دیا! |
| 8 | **Mistake warning** | فیڈ میں پھپھوند؟ یہ غلطی جانور کھا جاتی ہے |
| 9 | **Season urgency** | قربانی سے پہلے یہ 3 کام کر لیں |
| 10 | **Comparison** | 20 لاکھ کے بچھڑے کو عام دودھ؟ |
| 11 | **Secret / insider** | بڑے فارم والے یہ پاؤڈر کیوں لیتے ہیں؟ |
| 12 | **Price shock** | 55 ہزار کا بورا… پھر بھی ڈیمانڈ پر |
| 13 | **Before → after** | 2 مہینے پہلے اور آج… |
| 14 | **Famous area / person** | انڈا موڑ کا مشہور فارم |
| 15 | **Turkey / imported** | ترکی کا زبردست ٹاکسن بائنڈر |

## Rules
1. **On-screen line in Urdu script**, 3–7 words, one idea; key word in Aslam (owner's combo with Noori).
   The spoken first line can be his natural Roman/Urdu speech; write both separately.
2. Name the **animal** (بکرا، بچھڑا، گائے، دودھ والی) and the **pain or gain** (وزن، دودھ، بھوک، جگر، ہاضمہ).
3. Specific beats generic: a number, a city, a customer name, a price, a time.
4. Only claims on the bag or said by the owner. No cure/disease promises; no medicine-drug promotion on TikTok.
5. Sound like him (`owais-voice`): "زبردست"، "رزلٹ ہے نا"، "بھائی"، "بڑے شوقین لوگ ہیں". No AI-sounding lines.
6. Score each with the 5 checks (1 point each): stops the thumb in 1 s? · pain/gain clear? · specific? ·
   readable in 1 glance (≤ 7 words)? · true to the video? Also run `python3 .claude/skills/ig-reel/hookscore.py`
   on a Roman version for a second opinion (it is English-biased; trust the 5 checks).

## Output format (keep it short for the owner's phone)
3 options (or the number asked), each: **Urdu heading** · (spoken first line) · score /5 · one-word why.
Mark your pick with ⭐. Then stop and let him choose.
