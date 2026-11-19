#!/usr/bin/env python3
"""Built-in sound effects, synthesised (no licence issues), cached in assets/sfx/.

    python tools/sfx.py            # make them all and list them
    python tools/sfx.py --play-list

Names: whoosh, whoosh_fast, swoosh_up, pop, click, tick, ding, ching, impact, boom, riser, glitch
In edit.json:  "sfx": [{"sound": "whoosh", "at": 3.2, "volume": 0.8}]  (or "file": "my.wav")
"""
import argparse
import wave
from pathlib import Path

from common import REPO

SR = 48000
DIR = REPO / "assets" / "sfx"
NAMES = ["whoosh", "whoosh_fast", "swoosh_up", "pop", "click", "tick", "swish", "trr", "ding", "ching", "impact", "boom", "riser", "glitch"]


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
    if name == "swish":  # soft, airy, very short: for caption words
        d = 0.22
        s = swept_noise(d, 900, 5000, 1.6, np, 9) * np.sin(np.linspace(0, np.pi, int(d * SR))) ** 2
        return s * 0.6
    if name == "trr":  # rapid ratchet clicks (map route drawing)
        d = 1.0
        n = int(d * SR)
        s = np.zeros(n)
        rng = np.random.default_rng(11)
        t = 0.0
        while t < d - 0.03:
            i = int(t * SR)
            L = int(0.012 * SR)
            tt = np.arange(L) / SR
            f = rng.uniform(2200, 3200)
            s[i:i + L] += (np.sin(2 * np.pi * f * tt) + rng.standard_normal(L) * 0.4) * np.exp(-tt * 380)
            t += 1 / rng.uniform(26, 34)
        return s * np.minimum(1, np.linspace(0, 6, n)) * np.minimum(1, np.linspace(6, 0, n))
    if name == "tick":  # very soft, short "tk" for captions
        d = 0.05
        t = np.arange(int(d * SR)) / SR
        s = np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 160) + np.random.default_rng(7).standard_normal(len(t)) * np.exp(-t * 300) * 0.3
        return s
    if name == "keys":  # iPhone keyboard typing: a burst of soft "tock" taps (~0.5 s, 6-7 keys)
        d = 0.55
        n = int(d * SR)
        s = np.zeros(n)
        rng = np.random.default_rng(21)
        t = 0.0
        while t < d - 0.05:
            i = int(t * SR)
            L = int(0.03 * SR)
            tt = np.arange(L) / SR
            f = rng.uniform(1500, 2100)
            tap = (np.sin(2 * np.pi * f * tt) * 0.7 + rng.standard_normal(L) * 0.35) * np.exp(-tt * 260)
            s[i:i + L] += tap * rng.uniform(0.75, 1.0)
            t += rng.uniform(0.065, 0.095)
        return s * 0.8
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


# earshot (github.com/Leonxlnx/earshot, MIT): a bank of 252 pro-grade sound effects rendered from code.
# Use any bank id directly ("whoosh_fast/crisp", "pro_pop/bloop" ...: `earshot sfx list`), or set the style /
# edit option "sfx_bank": "pro" to upgrade our classic names to these.
PRO = {"whoosh": "pro_whoosh_big/swell", "whoosh_fast": "whoosh_fast/crisp", "swoosh_up": "pro_riser/air_gate",
       "pop": "pro_pop_in/round", "click": "pro_click/soft", "ding": "pro_notify/ding_2045", "ching": "notify/mid_tine",
       "impact": "pro_impact/short", "boom": "sub_drop/punch", "riser": "pro_riser/roll", "glitch": "pro_glitch/standard",
       "keys": "pro_typing_run/soft", "swish": "swish/soft", "tick": "hover_tick/mid"}


def earshot_render(sid: str) -> Path:
    import shutil
    import subprocess
    path = DIR / "earshot" / (sid.replace("/", "__") + ".wav")
    if not path.exists():
        if not shutil.which("earshot"):
            raise SystemExit("earshot is not installed: pip install git+https://github.com/Leonxlnx/earshot")
        path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["earshot", "sfx", "render", sid, "-o", str(path), "--sr", "48000"], check=True, capture_output=True)
    return path


def get(name: str, bank: str = "") -> Path:
    if "/" in name:  # an earshot bank id
        return earshot_render(name)
    if bank == "pro" and name in PRO:
        return earshot_render(PRO[name])
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
