#!/usr/bin/env python3
"""Transcribe speech with Whisper (faster-whisper), with a timestamp for every word.

    python tools/transcribe.py "Video Edits/Raw/my-reel/clip1.mp4" --project my-reel --language ur

Writes to Video Edits/Export/<project>/work/transcripts/:
    <clip>.json   segments + words with start/end times (used by captions.py)
    <clip>.srt    normal subtitle file, easy to read and correct

Models (first run downloads them): tiny, base, small (default), medium, large-v3.
Bigger = more accurate, slower. For Urdu, use at least 'medium'.
"""
import argparse

from common import EDITS, REPO, die, file_key, resolve, save_json


def srt_time(t: float) -> str:
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("media", nargs="+", help="video or audio files")
    ap.add_argument("--project", required=True)
    ap.add_argument("--language", default=None, help="ur, en, hi ... (default: auto-detect)")
    ap.add_argument("--model", default="small")
    ap.add_argument("--force", action="store_true", help="re-transcribe even if a transcript exists")
    args = ap.parse_args()

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        die("faster-whisper is not installed. Run: pip install -r requirements.txt")

    out_dir = EDITS / "Export" / args.project / "work" / "transcripts"
    model = None
    for item in args.media:
        src = resolve(item)
        if not src.exists():
            die(f"file not found: {src}")
        dest = out_dir / f"{file_key(src)}.json"
        if dest.exists() and not args.force:
            print(f"skip (already done): {src.name}")
            continue
        if model is None:
            print(f"Loading Whisper model '{args.model}' ...")
            model = WhisperModel(args.model, device="auto", compute_type="auto")
        print(f"Transcribing {src.name} ...")
        segments, info = model.transcribe(str(src), language=args.language, word_timestamps=True, vad_filter=True)
        segs = []
        for s in segments:
            words = [{"start": round(w.start, 3), "end": round(w.end, 3), "text": w.word.strip()}
                     for w in (s.words or []) if w.word.strip()]
            segs.append({"start": round(s.start, 3), "end": round(s.end, 3), "text": s.text.strip(), "words": words})
        save_json(dest, {"source": src.relative_to(REPO).as_posix() if src.is_relative_to(REPO) else str(src),
                         "language": info.language, "model": args.model, "segments": segs})
        srt = [f"{i}\n{srt_time(s['start'])} --> {srt_time(s['end'])}\n{s['text']}\n" for i, s in enumerate(segs, 1)]
        dest.with_suffix(".srt").write_text("\n".join(srt), encoding="utf-8")
        print(f"  {len(segs)} segments, language '{info.language}' -> {dest.relative_to(REPO)}")


if __name__ == "__main__":
    main()
