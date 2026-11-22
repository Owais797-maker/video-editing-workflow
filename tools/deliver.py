#!/usr/bin/env python3
"""Make the ONE file the owner gets on his iPhone: full resolution (4K stays 4K), one part, small enough that the
Claude app downloads it reliably (target <= 55 MB; files of 70-95 MB failed to download on 2026-11-22).

    python3 tools/deliver.py "Video Edits/Export/<name>/<name>.mp4"   ->  <name>-iphone.mp4  (+ prints size and SSIM)

Master already <= 55 MB: copied with faststart. Otherwise: HEVC (iPhone's own format, hvc1), 2-pass, preset slow,
bitrate chosen to land at the target size (capped at 45 Mb/s), AAC 256k. SSIM vs master is printed for the record.
"""
import json, subprocess, sys, shutil
from pathlib import Path

TARGET_MB = 55


def probe(p):
    j = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size", "-of", "json", str(p)],
                                  capture_output=True, text=True).stdout)
    return float(j["format"]["duration"]), int(j["format"]["size"])


def main():
    src = Path(sys.argv[1]); out = src.with_name(src.stem + "-iphone.mp4")
    dur, size = probe(src)
    if size <= TARGET_MB * 1e6:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-c", "copy", "-movflags", "+faststart", str(out)], check=True)
    else:
        audio_k = 256
        vk = int(min(45000, (TARGET_MB * 8e6 * 0.97 / dur) / 1000 - audio_k))
        log = src.with_name(".x265pass")
        common = ["-c:v", "libx265", "-preset", "slow", "-b:v", f"{vk}k", "-tag:v", "hvc1", "-pix_fmt", "yuv420p"]
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), *common, "-x265-params", f"pass=1:stats={log}:log-level=error",
                        "-an", "-f", "mp4", "/dev/null"], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), *common, "-x265-params", f"pass=2:stats={log}:log-level=error",
                        "-c:a", "aac", "-b:a", f"{audio_k}k", "-movflags", "+faststart", str(out)], check=True)
        for f in src.parent.glob(".x265pass*"):
            f.unlink()
    _, osz = probe(out)
    r = subprocess.run(["ffmpeg", "-i", str(out), "-i", str(src), "-lavfi", "[0:v][1:v]ssim", "-f", "null", "-"], capture_output=True, text=True)
    ssim = r.stderr.split("All:")[-1].split()[0] if "All:" in r.stderr else "?"
    print(f"{out}  {osz/1e6:.1f} MB  SSIM {ssim}")


if __name__ == "__main__":
    main()
