#!/usr/bin/env python3
"""Download YouTube videos, audios, and subtitles using yt-dlp and ffmpeg."""

import re
import json
import tempfile
import subprocess
from pathlib import Path

from parallel_download import with_retry


def _run_yt_dlp(args: list[str]) -> subprocess.CompletedProcess:
    """Run yt-dlp with the given arguments and return the result."""
    try:
        return subprocess.run(
            ["yt-dlp", *args],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        msg = (e.stderr.strip() or e.stdout.strip()).replace("Usage: yt-dlp [OPTIONS] URL [URL...]\n", "").strip()
        raise RuntimeError(f"Error running yt-dlp command: {msg}") from e
    except FileNotFoundError as e:
        raise RuntimeError("yt-dlp is not installed") from e


def get_video_info(url: str) -> dict:
    """Return a YouTube video's information as a dict, or a specific field from it."""
    result = _run_yt_dlp(["--dump-json", url])
    return json.loads(result.stdout)


@with_retry()
def download_video(url: str, file_format: str = "mp4", quality: str = "best", output_dir: str|Path = ".") -> Path:
    """Download a YouTube video and return the file's path."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    p_pattern = r"^(144|240|360|480|540|720|1080|1440|2160|4320)p$"
    k_pattern = r"^(2|4|8)k$"
    k_to_p = {"2": "1440", "4": "2160", "8": "4320"}

    quality = quality.strip().lower()
    if quality == "best":
        format_filter = f"bv*[ext={file_format}]+ba / bv*+ba / best"
    elif re.match(p_pattern, quality, re.IGNORECASE):
        height = quality[:-1]
        format_filter = f"bv*[ext={file_format}][height<={height}]+ba / bv*[height<={height}]+ba / best[height<={height}]"
    elif re.match(k_pattern, quality, re.IGNORECASE):
        height = k_to_p[quality[:-1]]
        format_filter = f"bv*[ext={file_format}][height<={height}]+ba / bv*[height<={height}]+ba / best[height<={height}]"
    else:
        raise ValueError(f"Invalid quality: {quality}")

    result = _run_yt_dlp([
        "-P", str(output_dir),
        "-o", f"%(title)s.%(ext)s",
        "-f", format_filter,
        "--merge-output-format", file_format,
        "--print", "after_move:filepath",
        "--no-warnings",
        url,
    ])
    
    filepath = Path(result.stdout.strip())

    return filepath


@with_retry()
def download_audio(url: str, file_format: str = "mp3", quality: str = "best", output_dir: str|Path = ".") -> Path:
    """Download the audio of a YouTube video and return the file's path."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if quality == "best":
        quality = "0"

    result = _run_yt_dlp([
        "-x",
        "-P", str(output_dir),
        "-o", f"%(title)s.%(ext)s",
        "-f", f"ba[ext={file_format}] / ba / best",
        "--audio-format", file_format,
        "--audio-quality", quality,
        "--print", "after_move:filepath",
        "--no-warnings",
        url,
    ])
    
    filepath = Path(result.stdout.strip())

    return filepath


@with_retry()
def download_subtitles(url: str, file_format: str = "srt", language: str|None = None, output_dir: str|Path = ".") -> Path:
    """Download the subtitles of a YouTube video and return the file's path."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    video_info = get_video_info(url)
    language = (language if language is not None else video_info.get("language")) or "en"
    manual_subs = video_info.get("subtitles", {})
    automatic_subs = video_info.get("automatic_captions", {})
    if subs := manual_subs or automatic_subs:
        matching = next((lang for lang in subs if lang.startswith(language)), None)
    else:
        raise RuntimeError(f"Video does not have subtitles: {url}")

    result = _run_yt_dlp([
        "-P", f"subtitle:{output_dir}",
        "-o", f"subtitle:%(title)s.%(ext)s",
        "--write-subs" if manual_subs else "--write-auto-subs",
        "--sub-langs", matching,
        "--sub-format", f"{file_format}/best",
        "--convert-subs", file_format,
        "--print", "%(title)s",
        "--no-simulate",
        "--skip-download",
        "--no-warnings",
        url,
    ])

    title = result.stdout.strip()
    filename = f"{title}.{matching}.{file_format}"
    filepath = Path(output_dir) / filename

    return filepath


@with_retry()
def download_transcript(url: str, language: str|None = None, output_dir: str|Path = ".") -> Path:
    """Download a plain-text transcript from a YouTube video."""
    with tempfile.TemporaryDirectory() as tmpdir:
        srt_path = download_subtitles(url, output_dir=tmpdir, language=language, file_format="srt")
        with open(srt_path, encoding="utf-8") as f:
            srt_lines = f.readlines()

    txt_path = Path(output_dir) / srt_path.with_suffix(".txt").name

    index_pattern = r"^\d+$"
    timestamp_pattern = r"\d{2,}:[0-5]\d:[0-5]\d,\d{3}"
    interval_pattern = rf"^{timestamp_pattern} --> {timestamp_pattern}$"

    with open(txt_path, "w") as f:
        current_text = []
        for line in srt_lines:
            line = line.rstrip("\n")
            if line and not (re.match(index_pattern, line) or re.match(interval_pattern, line)):
                current_text.append(line)
            elif current_text:
                f.write(" ".join(current_text) + "\n")
                current_text = []
        if current_text:
            f.write(" ".join(current_text) + "\n")

    return txt_path
