# Naat audio: making a phone recording sound like a studio

The owner is a naat khwan. When they send a recording, Claude cleans and polishes it.

## What can be done (in this cloud setup)
- **Noise removal:** fans, AC hum, traffic, hiss (AI denoiser such as DeepFilterNet, or
  FFmpeg `afftdn` / `arnndn`); hum filters for 50 Hz electrical buzz.
- **Room echo reduction:** partial: an untreated room's echo can be reduced, not fully removed.
- **Voice polish:** high-pass (remove rumble), gentle EQ (warmth around 150–250 Hz, presence
  at 3–5 kHz, air at 10–12 kHz), de-esser for harsh "s" sounds, compression for even level.
- **Studio ambience:** a tasteful hall/plate reverb (naats usually sound best with a warm,
  long hall), optional light delay/echo on line endings, stereo widening.
- **Loudness:** final mix at -14 LUFS (social media), true peak -1 dB, no clipping.
- **Daf / background separation:** if a recording has music or crowd, the voice can be
  separated (AI stem separation, e.g. Demucs) before processing.

## What cannot be fixed
Distortion from shouting too close to the mic, clipped peaks, heavy wind noise, or a voice
buried under loud background sound can be improved but not made truly "studio".

## Recording tips (biggest difference comes from the source)
- Record in a small room with soft things (curtains, mattress, cupboard of clothes).
- Phone or lav mic 15–20 cm from the mouth, slightly to the side; Voice Memos app in
  "Lossless" quality on iPhone (Settings → Voice Memos → Audio Quality → Lossless).
- Turn off fans/AC, phone on airplane mode, record 5 s of silence first (helps denoising).
- Keep the same distance throughout; for high notes, lean back a little instead of shouting.
