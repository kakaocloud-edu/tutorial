"""Rebuild the scroll film from an approved master without resizing or cropping.

Requires Python 3 and FFmpeg with libaom-av1/libwebp; no Python packages needed.
    python tools/extract_scroll_film.py /path/to/master.mp4 --visible-mark-cleaned
    python tools/extract_scroll_film.py /path/to/master.mp4 --format webp

AVIF CRF 20 is the default. The WebP poster remains available to browsers without
AVIF support. All frames are staged and fully decoded before replacing the old
sequence. AVIF extraction uses temporary raw YUV, preserving the master pixels
without an intermediate RGB conversion. The scratch file is deleted afterward.

FFmpeg is found on PATH or via --ffmpeg / FFMPEG. Its sibling ffprobe is used
when available; --ffprobe / FFPROBE can override it. --visible-mark-cleaned only
records that the input master has already been cleaned; this tool adds no edits.
"""

from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time


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
    parser.add_argument("--format", choices=("avif", "webp"), default="avif")
    parser.add_argument("--crf", type=int, default=20, help="AVIF quality, 0 to 63")
    parser.add_argument("--cpu-used", type=int, default=6)
    parser.add_argument("--quality", type=int, default=82, help="WebP sequence quality")
    parser.add_argument("--compression-level", type=int, default=6, help="WebP compression effort")
    parser.add_argument("--poster-quality", type=int, default=82)
    parser.add_argument("--workers", type=int, default=4, help="Parallel AVIF encode/decode jobs, 1 to 4")
    parser.add_argument("--threads", type=int, default=2, help="Threads per encode")
    parser.add_argument("--ffmpeg")
    parser.add_argument("--ffprobe")
    parser.add_argument("--visible-mark-cleaned", action="store_true",
                        help="Record that the master already has its visible corner mark cleaned")
    parser.add_argument("--clip-boundaries", type=float, nargs="*", default=[7.8, 15.6],
                        help="Clip crossfade start times, in seconds")
    args = parser.parse_args()
    if not 0 <= args.crf <= 63 or not 0 <= args.cpu_used <= 8:
        parser.error("AVIF requires --crf 0..63 and --cpu-used 0..8")
    if not all(0 <= value <= 100 for value in (args.quality, args.poster_quality)):
        parser.error("WebP quality must be between 0 and 100")
    if not 0 <= args.compression_level <= 6 or not 1 <= args.workers <= 4 or args.threads < 1:
        parser.error("Use --compression-level 0..6, --workers 1..4, and positive --threads")
    source = args.source.resolve(strict=True)
    output = args.output.resolve()
    ffmpeg = executable("ffmpeg", args.ffmpeg)
    ffprobe = executable("ffprobe", args.ffprobe, ffmpeg)

    def run(command, **kwargs):
        return subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin", *command],
                              check=True, capture_output=True, **kwargs)

    metadata = json.loads(subprocess.run([
        ffprobe, "-v", "error", "-count_frames", "-select_streams", "v:0",
        "-show_entries", "stream=width,height,avg_frame_rate,nb_read_frames,duration",
        "-of", "json", str(source),
    ], check=True, capture_output=True, text=True).stdout)["streams"][0]
    count = int(metadata["nb_read_frames"])
    width, height = int(metadata["width"]), int(metadata["height"])
    fps = Fraction(metadata["avg_frame_rate"])
    if count < 2 or fps <= 0 or width % 2 or height % 2:
        raise ValueError("The master needs at least two frames, a known frame rate, and even dimensions")
    output.parent.mkdir(parents=True, exist_ok=True)
    frame_size = width * height * 3 // 2
    scratch_bytes = frame_size * count if args.format == "avif" else 0
    # Include space for encoded frames and leave 64 MiB available during staging.
    required = scratch_bytes + max(source.stat().st_size * 2, 64 * 1024 * 1024)
    free = shutil.disk_usage(output.parent).free
    if free < required:
        raise OSError(f"Need {required:,} free bytes for staging; only {free:,} available")
    print(json.dumps({"format": args.format, "frames": count, "scratchBytes": scratch_bytes,
                      "freeBytes": free}), flush=True)
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="scroll-film-", dir=output.parent) as temporary:
        staging = Path(temporary)
        expected = [f"frame-{index:03d}.{args.format}" for index in range(count)]
        frames = [staging / name for name in expected]
        if args.format == "avif":
            raw = staging / "source.yuv"
            run(["-i", str(source), "-map", "0:v:0", "-an", "-fps_mode", "passthrough",
                 "-pix_fmt", "yuv420p", "-f", "rawvideo", str(raw)])
            if raw.stat().st_size != scratch_bytes:
                raise RuntimeError("Decoded scratch data does not match the source frame count")

            def encode(index):
                with raw.open("rb") as stream:
                    stream.seek(index * frame_size)
                    pixels = stream.read(frame_size)
                run(["-f", "rawvideo", "-pixel_format", "yuv420p", "-video_size", f"{width}x{height}",
                     "-framerate", str(fps), "-i", "pipe:0", "-frames:v", "1", "-an",
                     "-c:v", "libaom-av1", "-crf", str(args.crf), "-b:v", "0",
                     "-cpu-used", str(args.cpu_used), "-still-picture", "1", "-pix_fmt", "yuv420p",
                     "-threads", str(args.threads), str(frames[index])], input=pixels)

            with ThreadPoolExecutor(max_workers=args.workers) as pool:
                for finished, _ in enumerate(pool.map(encode, range(count)), 1):
                    if finished % 50 == 0 or finished == count:
                        print(f"Encoded {finished}/{count} frames", flush=True)
            raw.unlink()
        else:
            run(["-i", str(source), "-map", "0:v:0", "-an", "-fps_mode", "passthrough",
                 "-start_number", "0", "-c:v", "libwebp", "-quality", str(args.quality),
                 "-compression_level", str(args.compression_level), "-threads", str(args.threads),
                 str(staging / "frame-%03d.webp")])
        if [path.name for path in sorted(staging.glob(f"frame-*.{args.format}"))] != expected:
            raise RuntimeError("Extracted filenames do not match the source frame count")

        def validate(path):
            decoded = run(["-i", str(path), "-frames:v", "1", "-f", "framemd5", "pipe:1"], text=True).stdout
            dimensions = f"#dimensions 0: {width}x{height}"
            rows = [line for line in decoded.splitlines() if line and not line.startswith("#")]
            if dimensions not in decoded or len(rows) != 1:
                raise RuntimeError(f"Invalid frame or dimensions: {path.name}")

        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            for finished, _ in enumerate(pool.map(validate, frames), 1):
                if finished % 100 == 0 or finished == count:
                    print(f"Validated {finished}/{count} frames", flush=True)
        # Encode the static fallback directly from the final master frame, not
        # from the lossy AVIF, so fallback fidelity is independent of the format.
        poster = staging / "poster.webp"
        run(["-i", str(source), "-vf", f"select='eq(n,{count - 1})'", "-frames:v", "1", "-an",
             "-c:v", "libwebp", "-quality", str(args.poster_quality), "-compression_level", "6",
             "-threads", str(args.threads), str(poster)])
        validate(poster)
        sizes = [frame.stat().st_size for frame in frames]
        manifest = {
            "count": count, "width": width, "height": height, "fps": float(fps),
            "duration": float(Fraction(count, 1) / fps), "source": source.name,
            "sourceSha256": sha256(source), "format": args.format,
            "encoder": "libaom-av1" if args.format == "avif" else "libwebp",
            "pixelFormat": "yuv420p", "framePattern": f"frame-%03d.{args.format}",
            "startIndex": 0, "poster": "poster.webp", "posterFormat": "webp",
            "posterEncoder": "libwebp", "posterQuality": args.poster_quality,
            "posterCompressionLevel": 6, "threads": args.threads,
            "clipBoundariesSeconds": args.clip_boundaries, "clipCrossfadeSeconds": 0.2,
            "frameBytes": sum(sizes), "largestFrameBytes": max(sizes),
            "attributionPreserved": not args.visible_mark_cleaned,
            "visibleWatermarkRemoved": args.visible_mark_cleaned, "crop": False,
        }
        if args.format == "avif":
            manifest.update({"crf": args.crf, "cpuUsed": args.cpu_used})
        else:
            manifest.update({"quality": args.quality, "compressionLevel": args.compression_level})
        manifest_path = staging / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        output.mkdir(exist_ok=True)
        for artifact in [*frames, poster]:
            artifact.replace(output / artifact.name)
        manifest_path.replace(output / manifest_path.name)
        # Delete only obsolete generated frames, after successful full decoding
        # and installing the complete replacement. Never touch unrelated files.
        for previous in output.iterdir():
            if re.fullmatch(r"frame-\d{3,}\.(?:webp|avif)", previous.name) and previous.name not in expected:
                previous.unlink()
    print(json.dumps({"output": str(output), "elapsedSeconds": round(time.monotonic() - started, 2),
                      **manifest}, indent=2), flush=True)


if __name__ == "__main__":
    main()
