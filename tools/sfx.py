#!/usr/bin/env python3
"""Built-in sound effects, synthesised (no licence issues), cached in assets/sfx/.

    python tools/sfx.py            # make them all and list them
    python tools/sfx.py --play-list

Names: whoosh, whoosh_fast, swoosh_up, pop, click, ding, ching, impact, boom, riser, glitch
In edit.json:  "sfx": [{"sound": "whoosh", "at": 3.2, "volume": 0.8}]  (or "file": "my.wav")
"""
import argparse
import wave
from pathlib import Path

from common import REPO

SR = 48000
DIR = REPO / "assets" / "sfx"
NAMES = ["whoosh", "whoosh_fast", "swoosh_up", "pop", "click", "ding", "ching", "impact", "boom", "riser", "glitch"]


def _np():
    import numpy as np
    return np


def env(n, attack, release, np):
    e = np.ones(n)
    a, r = int(attack * SR), int(release * SR)
    if a:
        e[:a] = np.linspace(0, 1, a) ** 2
    if r:
        e[-r:] *= np.linspace(1, 0, r) ** 2
    return e


def swept_noise(dur, f0, f1, q, np, seed=1):
    """White noise through a resonant band-pass whose centre sweeps f0 -> f1 (state-variable filter)."""
    n = int(dur * SR)
    x = np.random.default_rng(seed).standard_normal(n)
    f = np.geomspace(f0, f1, n)
    g = 2 * np.sin(np.pi * f / SR)
    low = band = 0.0
    out = np.empty(n)
    damp = 1.0 / q
    for i in range(n):  # simple loop; sounds are short
        high = x[i] - low - damp * band
        band += g[i] * high
        low += g[i] * band
        out[i] = band
    return out / (np.abs(out).max() + 1e-9)


def tone(freq, dur, np, decay=6.0, partials=((1, 1.0),)):
    t = np.arange(int(dur * SR)) / SR
    s = sum(a * np.sin(2 * np.pi * freq * m * t) * np.exp(-decay * m ** 0.5 * t) for m, a in partials)
    return s


def make(name: str):
    np = _np()
    if name in ("whoosh", "whoosh_fast"):
        d = 0.55 if name == "whoosh" else 0.3
        s = swept_noise(d, 300, 3500, 2.5, np) * np.sin(np.linspace(0, np.pi, int(d * SR))) ** 1.5
        st = np.stack([s * np.linspace(1, 0.4, len(s)), s * np.linspace(0.4, 1, len(s))], 1)  # pans across
        return st * 0.8
    if name == "swoosh_up":
        d = 0.6
        s = swept_noise(d, 400, 8000, 4, np, 2) * env(int(d * SR), 0.4, 0.15, np)
        return s * 0.7
    if name == "pop":
        d = 0.12
        t = np.arange(int(d * SR)) / SR
        f = 900 * np.exp(-t * 25) + 250
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 40)
        return s * 0.9
    if name == "click":
        d = 0.04
        t = np.arange(int(d * SR)) / SR
        s = np.random.default_rng(3).standard_normal(len(t)) * np.exp(-t * 180) * 0.6 + np.sin(2 * np.pi * 2500 * t) * np.exp(-t * 120) * 0.5
        return s
    if name == "ding":
        return tone(1318.5, 1.4, np, 4.0, ((1, 1), (2.0, 0.35), (3.01, 0.2), (4.2, 0.08))) * 0.6
    if name == "ching":
        a = tone(2093, 0.9, np, 6.0, ((1, 1), (2.76, 0.4), (5.4, 0.2)))
        b = tone(2637, 0.9, np, 6.0, ((1, 1), (2.76, 0.4), (5.4, 0.2)))
        s = a.copy()
        off = int(0.07 * SR)
        s[off:] += b[: len(s) - off]
        return s * 0.35
    if name in ("impact", "boom"):
        d = 1.2 if name == "boom" else 0.6
        t = np.arange(int(d * SR)) / SR
        f = (55 if name == "boom" else 70) + 90 * np.exp(-t * 30)
        body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * (3 if name == "boom" else 7))
        hit = np.random.default_rng(4).standard_normal(len(t)) * np.exp(-t * 60) * 0.5
        return np.tanh((body + hit) * 1.5) * 0.85
    if name == "riser":
        d = 1.5
        t = np.arange(int(d * SR)) / SR
        f = np.geomspace(200, 1600, len(t))
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3 + swept_noise(d, 500, 9000, 3, np, 5) * 0.5
        return s * env(len(t), 1.2, 0.05, np) * 0.7
    if name == "glitch":
        d = 0.25
        rng = np.random.default_rng(6)
        t = np.arange(int(d * SR)) / SR
        s = np.sign(np.sin(2 * np.pi * rng.choice([200, 400, 800, 1600], len(t) // 600 + 1).repeat(600)[: len(t)] * t))
        s *= (rng.random(len(t) // 1200 + 1) > 0.3).repeat(1200)[: len(t)]
        return s * 0.25
    raise KeyError(name)


def write(path: Path, s) -> None:
    np = _np()
    if s.ndim == 1:
        s = np.stack([s, s], 1)
    s = s / (np.abs(s).max() + 1e-9) * 0.89  # same peak level for every sound
    s = np.clip(s, -1, 1)
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((s * 32767).astype("<i2").tobytes())


def get(name: str) -> Path:
    path = DIR / f"{name}.wav"
    if not path.exists():
        write(path, make(name))
    return path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.parse_args()
    for n in NAMES:
        print(f"{n:12s} {get(n).relative_to(REPO)}")


if __name__ == "__main__":
    main()
