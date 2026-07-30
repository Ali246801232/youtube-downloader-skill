#!/usr/bin/env python3
"""Download YouTube videos, audios, and subtitles using yt-dlp and ffmpeg."""

import re
import json
import tempfile
import subprocess
import unicodedata
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
        raise RuntimeError(f"Error running yt-dlp command: {e.stderr.strip() or e.stdout.strip()}") from e
    except FileNotFoundError as e:
        raise RuntimeError("yt-dlp is not installed") from e


def get_video_info(url: str) -> dict:
    """Return a YouTube video's information as a dict, or a specific field from it."""
    result = _run_yt_dlp(["--dump-json", url])
    return json.loads(result.stdout)


# TODO: Re-implement
@with_retry()
def download_video(url: str, file_format: str = "mp4", quality: str = "best", language: str|None = None, output_dir: str|Path = ".") -> Path:
    """Download a YouTube video and return the file's path."""
    pass


# TODO: Re-implement
@with_retry()
def download_audio(url: str, quality: str = "192K", language: str|None = None, file_format: str = "mp3", output_dir: str|Path = ".") -> Path:
    """Download the audio of a YouTube video and return the file's path."""
    pass


@with_retry()
def download_subtitles(url: str, file_format: str = "srt", language: str|None = None, output_dir: str|Path = ".") -> Path:
    """Download the subtitles of a YouTube video and return the file's path."""
    video_info = get_video_info(url)
    video_title = _sanitize_title(video_info.get("title"))
    video_id = video_info.get("id")

    language = (language if language is not None else video_info.get("language")) or "en"
    manual_subs = video_info.get("subtitles", {})
    automatic_subs = video_info.get("automatic_captions", {})
    if manual_subs:
        has_manual = True
        if language in manual_subs:
            matching = language
        else:
            matching = next((lang for lang in manual_subs if lang.startswith(language)), None)
        output_path = Path(output_dir) / f"{video_title}.from_manual_subs"
    elif automatic_subs:
        has_manual = False
        if language in automatic_subs:
            matching = language
        else:
            matching = next((lang for lang in automatic_subs if lang.startswith(language)), None)
        output_path = Path(output_dir) / f"{video_title}.from_automatic_subs"
    else:
        raise RuntimeError(f"Video does not have subtitles: {video_title} [{video_id}]")

    _run_yt_dlp([
        "--write-subs" if has_manual else "--write-auto-subs",
        "--sub-langs", matching,
        "--convert-subs", file_format,
        "--skip-download",
        "-o", f"{output_path}.%(ext)s",
        "--no-warnings",
        url,
    ])

    return output_path.with_name(f"{output_path.name}.{matching}.{file_format}")


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
            if re.match(index_pattern, line):
                continue
            if re.match(interval_pattern, line):
                continue
            if not line:
                if current_text:
                    f.write(" ".join(current_text) + "\n")
                    current_text = []
                continue
            current_text.append(line)
        if current_text:
            f.write(" ".join(current_text) + "\n")

    return txt_path
