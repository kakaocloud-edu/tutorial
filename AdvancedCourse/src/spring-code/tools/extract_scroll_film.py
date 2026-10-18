"""Extract a source film into the root page's scroll-scrubbed WebP sequence.

Requires Python 3 and FFmpeg with libwebp. No Python packages are required.
Run from any directory, for example:
    python tools/extract_scroll_film.py /path/to/approved-preview.mp4

FFmpeg is found on PATH or via --ffmpeg / FFMPEG. Its sibling ffprobe is used
when available; --ffprobe / FFPROBE can override it. The source image area is
preserved without cropping. Use --visible-mark-cleaned to record an input
master whose visible corner mark has already been cleaned separately.
"""

import argparse
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


DEFAULT_OUTPUT = (Path(__file__).resolve().parents[1]
                  / "src/main/resources/static/experience/film")


def executable(name, explicit=None, sibling=None):
    requested = explicit or os.environ.get(name.upper())
    if requested:
        resolved = shutil.which(requested) or requested
        if Path(resolved).is_file():
            return str(Path(resolved).resolve())
        raise FileNotFoundError(f"Cannot find {name}: {requested}")
    if sibling:
        candidate = Path(sibling).with_name(name + Path(sibling).suffix)
        if candidate.is_file():
            return str(candidate)
    resolved = shutil.which(name)
    if not resolved:
        raise FileNotFoundError(f"Install {name} or pass --{name} with its path")
    return resolved


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Approved master video")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--quality", type=int, default=82)
    parser.add_argument("--ffmpeg")
    parser.add_argument("--ffprobe")
    parser.add_argument("--visible-mark-cleaned", action="store_true",
                        help="Record that the input master already has its visible corner mark cleaned")
    parser.add_argument("--clip-boundaries", type=float, nargs="*", default=[7.8, 15.6],
                        help="Clip crossfade start times, in seconds")
    args = parser.parse_args()
    source = args.source.resolve(strict=True)
    output = args.output.resolve()
    if not 0 <= args.quality <= 100:
        parser.error("--quality must be between 0 and 100")
    ffmpeg = executable("ffmpeg", args.ffmpeg)
    ffprobe = executable("ffprobe", args.ffprobe, ffmpeg)
    metadata = json.loads(subprocess.run([
        ffprobe, "-v", "error", "-count_frames", "-select_streams", "v:0",
        "-show_entries", "stream=width,height,avg_frame_rate,nb_read_frames,duration",
        "-of", "json", str(source),
    ], check=True, capture_output=True, text=True).stdout)["streams"][0]
    count = int(metadata["nb_read_frames"])
    fps = Fraction(metadata["avg_frame_rate"])
    if count < 2 or fps <= 0:
        raise ValueError("The master must have at least two frames and a known frame rate")
    output.parent.mkdir(parents=True, exist_ok=True)
    # Extract completely before replacing the sequence; a failed encode leaves
    # the existing preview usable. Only known generated files are replaced.
    with tempfile.TemporaryDirectory(prefix="scroll-film-", dir=output.parent) as temporary:
        staging = Path(temporary)
        subprocess.run([
            ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin", "-i", str(source),
            "-map", "0:v:0", "-an", "-fps_mode", "passthrough", "-start_number", "0",
            "-c:v", "libwebp", "-quality", str(args.quality), "-compression_level", "5",
            "-threads", "4", str(staging / "frame-%03d.webp"),
        ], check=True)
        frames = sorted(staging.glob("frame-*.webp"))
        expected = [f"frame-{index:03d}.webp" for index in range(count)]
        if [frame.name for frame in frames] != expected:
            raise RuntimeError("Extracted frames do not match the source frame count")
        shutil.copyfile(frames[-1], staging / "poster.webp")
        sizes = [frame.stat().st_size for frame in frames]
        manifest = {
            "count": count,
            "width": int(metadata["width"]),
            "height": int(metadata["height"]),
            "fps": float(fps),
            "duration": float(Fraction(count, 1) / fps),
            "source": source.name,
            "sourceSha256": sha256(source),
            "framePattern": "frame-%03d.webp",
            "startIndex": 0,
            "poster": "poster.webp",
            "quality": args.quality,
            "clipBoundariesSeconds": args.clip_boundaries,
            "clipCrossfadeSeconds": 0.2,
            "frameBytes": sum(sizes),
            "largestFrameBytes": max(sizes),
            "attributionPreserved": not args.visible_mark_cleaned,
            "visibleWatermarkRemoved": args.visible_mark_cleaned,
            "crop": False,
        }
        (staging / "manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        output.mkdir(exist_ok=True)
        for previous in output.glob("frame-*.webp"):
            if previous.name not in expected:
                previous.unlink()
        for artifact in staging.iterdir():
            artifact.replace(output / artifact.name)
    print(json.dumps({"output": str(output), **manifest}, indent=2))


if __name__ == "__main__":
    main()
