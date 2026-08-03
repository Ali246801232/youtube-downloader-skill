#!/usr/bin/env python3
"""Download YouTube videos, audios, and subtitles using yt-dlp and ffmpeg."""

import re
import json
import tempfile
import subprocess
import unicodedata
from pathlib import Path

from extract_urls import find_video_urls, find_playlist_urls, find_channel_urls
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
        raise FileNotFoundError("yt-dlp is not installed") from e


def _sanitize_title(title: str) -> str:
    """Return a given YouTube video title sanitized."""
    sanitized = title
    sanitized = unicodedata.normalize("NFKD", sanitized).encode("utf-8", "ignore").decode("utf-8")
    sanitized = re.sub(r"[\/\\:*?\"<>|]", " ", sanitized)
    sanitized = sanitized.strip("_. ")
    if not sanitized:
        return "untitled"
    return sanitized


def get_info(url: str) -> dict:
    """Return a YouTube video, playlist, or channel URL's metadata as a dict."""
    if match := find_video_urls(url, fullmatch=True):
        return json.loads(_run_yt_dlp(["--dump-json", "--write-auto-subs", match]).stdout)
    elif match := find_playlist_urls(url, fullmatch=True):
        return json.loads(_run_yt_dlp(["--dump-single-json", "--flat-playlist", match]).stdout)
    elif match := find_channel_urls(url, fullmatch=True):
        return json.loads(_run_yt_dlp(["--dump-single-json", match]).stdout)
    else:
        raise ValueError(f"{url} is not a YouTube video, playlist, or channel URL")


@with_retry(retry_on_exceptions=[RuntimeError])
def download_video(url: str, file_format: str, quality: str, output_dir: str|Path) -> Path:
    """Download a YouTube video and return the file's path."""
    if not (url := find_video_urls(url, fullmatch=True)):
        raise ValueError(f"{url} is not a YouTube video URL")

    output_dir = Path(output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    p_pattern = r"^(144|240|360|480|540|720|1080|1440|2160|4320)p$"
    k_pattern = r"^(2|4|8)k$"
    k_to_p = {"2": "1440", "4": "2160", "8": "4320"}

    quality = quality.strip().lower()
    if quality == "best":
        format_filter = f"bv*[ext={file_format}]+ba / bv*+ba / best"
    elif re.match(p_pattern, quality, flags=re.IGNORECASE):
        height = quality[:-1]
        format_filter = f"bv*[ext={file_format}][height<={height}]+ba / bv*[height<={height}]+ba / best[height<={height}]"
    elif re.match(k_pattern, quality, flags=re.IGNORECASE):
        height = k_to_p[quality[:-1]]
        format_filter = f"bv*[ext={file_format}][height<={height}]+ba / bv*[height<={height}]+ba / best[height<={height}]"
    else:
        raise ValueError(f"Invalid quality: {quality}")

    video_info = get_info(url)
    title = _sanitize_title(video_info.get("title"))

    _run_yt_dlp([
        "-P", str(output_dir),
        "-o", f"{title}.%(ext)s",
        "-f", format_filter,
        "--merge-output-format", file_format,
        "--remux-video", file_format,
        "--no-warnings",
        url,
    ])

    output_path = output_dir / f"{title}.{file_format}"
    if output_path.exists() and output_path.is_file():
        return output_path
    raise RuntimeError(f"Failed to verify final output file for {url} at {output_path}")



@with_retry(retry_on_exceptions=[RuntimeError])
def download_audio(url: str, file_format: str, quality: str, output_dir: str|Path) -> Path:
    """Download the audio of a YouTube video and return the file's path."""
    if not (url := find_video_urls(url, fullmatch=True)):
        raise ValueError(f"{url} is not a YouTube video URL")

    output_dir = Path(output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if quality == "best":
        quality = "0"

    video_info = get_info(url)
    title = _sanitize_title(video_info.get("title"))

    _run_yt_dlp([
        "-x",
        "-P", str(output_dir),
        "-o", f"{title}.%(ext)s",
        "-f", f"ba[ext={file_format}] / ba / best",
        "--audio-format", file_format,
        "--audio-quality", quality,
        "--no-warnings",
        url,
    ])

    output_path = output_dir / f"{title}.{file_format}"
    if output_path.exists() and output_path.is_file():
        return output_path
    raise RuntimeError(f"Failed to verify final output file for {url} at {output_path}")


@with_retry(retry_on_exceptions=[RuntimeError])
def download_subtitles(url: str, file_format: str, output_dir: str|Path, language: str|None = None) -> Path:
    """Download the subtitles of a YouTube video and return the file's path."""
    if not (url := find_video_urls(url, fullmatch=True)):
        raise ValueError(f"{url} is not a YouTube video URL")

    output_dir = Path(output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    video_info = get_info(url)
    language = (language if language is not None else video_info.get("language")) or "en"
    manual_subs = video_info.get("subtitles", {})
    automatic_subs = video_info.get("automatic_captions", {})
    if not (automatic_subs or manual_subs):
        raise ValueError(f"{url} does not have subtitles")

    matching_manual = next((lang for lang in manual_subs if lang.startswith(language)), None)
    matching_automatic = next((lang for lang in automatic_subs if lang.startswith(language)), None)
    matching = matching_manual or matching_automatic
    if not matching:
        raise ValueError(f"{url} does not have subtitles in the language {language}")

    title = _sanitize_title(video_info.get("title"))

    _run_yt_dlp([
        "-P", f"subtitle:{output_dir}",
        "-o", f"subtitle:{title}.%(ext)s",
        "--write-subs" if matching_manual else "--write-auto-subs",
        "--sub-langs", matching,
        "--sub-format", f"{file_format}/best",
        "--convert-subs", file_format,
        "--skip-download",
        "--no-warnings",
        url,
    ])

    output_path = output_dir / f"{title}.{matching}.{file_format}"
    if output_path.exists() and output_path.is_file():
        return output_path
    raise RuntimeError(f"Failed to verify final output file for {url} at {output_path}")


@with_retry(retry_on_exceptions=[RuntimeError])
def download_transcript(url: str, output_dir: str|Path, language: str|None = None) -> Path:
    """Download a plain-text transcript from a YouTube video."""
    if not (url := find_video_urls(url, fullmatch=True)):
        raise ValueError(f"{url} is not a YouTube video URL")

    with tempfile.TemporaryDirectory() as tmpdir:
        srt_path = download_subtitles(url, output_dir=tmpdir, file_format="srt", language=language)
        with open(srt_path, encoding="utf-8") as f:
            srt_lines = f.readlines()

    output_path = Path(output_dir).expanduser().resolve() / srt_path.with_suffix(".txt").name

    index_pattern = r"^\d+$"
    timestamp_pattern = r"\d{2,}:[0-5]\d:[0-5]\d,\d{3}"
    interval_pattern = rf"^{timestamp_pattern} --> {timestamp_pattern}$"

    with open(output_path, "w", encoding="utf-8") as f:
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

    if output_path.exists() and output_path.is_file():
        return output_path
    raise RuntimeError(f"Failed to verify final output file for {url} at {output_path}")
