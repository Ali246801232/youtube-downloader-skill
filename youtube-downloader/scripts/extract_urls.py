#!/usr/bin/env python3
"""Extract YouTube video URLs from text string, a file, or a playlist."""

import re
import subprocess
from pathlib import Path


_VIDEO_URL_PATTERN = re.compile(
    r"(?:https?:\/\/)?"                  # https://, http://, ://
    r"(?:"                               # (
        r"(?:www\.|m\.)?youtube\.com\/"  #     www.youtube.com/, m.youtube.com/
        r"(?:"                           #     (
            r"watch\?(?:[^&\s]*&)*?v="   #         watch?v=, watch?[other query parameters]v=
            r"|"                         #         or
            r"shorts\/"                  #         shorts/
            r"|"                         #         or
            r"v\/"                       #         v/
        r")"                             #     )
        r"|"                             #     or
        r"youtu\.be\/"                   #     youtu.be/
    r")"                                 # )
    r"([a-zA-Z0-9_-]{11})"               # video ID (capturing group 1)
    r"(?:[?&]\S*)?"                      # other query parameters
)

_PLAYLIST_URL_PATTERN = re.compile(
    r"(?:https?:\/\/)?"                   # https://, http://, ://
    r"(?:"                                # (
        r"(?:www\.|m\.)?youtube\.com\/"   #     www.youtube.com/, m.youtube.com/
        r"playlist\?(?:[^&\s]*&)*?list="  #     playlist?list=, playlist?[other query parameters]list=
    r")"                                  # )
    r"([a-zA-Z0-9_-]+)"                   # playlist ID (capturing group 1)
    r"(?:[?&]\S*)?"                       # other query parameters
)


def is_video_url(text: str) -> bool:
    """Return whether a string is a YouTube video URL."""
    return bool(_VIDEO_URL_PATTERN.fullmatch(text.strip()))

def is_playlist_url(text: str) -> bool:
    """Return whether a string is a YouTube playlist URL."""
    return bool(_PLAYLIST_URL_PATTERN.fullmatch(text.strip()))


def extract_urls_from_text(text: str) -> list[str]:
    """Return a list of YouTube video URLs in a text string."""
    matches = _VIDEO_URL_PATTERN.findall(text)
    seen = set()
    urls = []
    for video_id in matches:
        if video_id not in seen:
            seen.add(video_id)
            urls.append(f"https://www.youtube.com/watch?v={video_id}")
    return urls


def extract_urls_from_file(file_path: str|Path) -> list[str]:
    """Return a list of YouTube video URLs in a file."""
    file_path = Path(file_path)
    if not(file_path.exists() and file_path.is_file()):
        raise RuntimeError(f"No file found at {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return extract_urls_from_text(file.read())
    except Exception as e:
        raise RuntimeError(f"Error extracting URLs from file {file_path}: {e}")


def extract_urls_from_playlist(playlist_url: str) -> list[str]:
    """Return a list of YouTube video URLs in a playlist using yt-dlp."""
    if not is_playlist_url(playlist_url):
        raise ValueError(f"Invalid playlist URL: {playlist_url}")

    try:
        result = subprocess.run(
            ["yt-dlp", "--flat-playlist", "--print", "id", playlist_url],
            capture_output=True, text=True, check=True
        )
    except FileNotFoundError as e:
        raise RuntimeError("yt-dlp is not installed") from e
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error fetching playlist from {playlist_url} using yt-dlp: {e.stderr.strip() or e.stdout.strip()}") from e

    urls = []
    seen = set()
    for line in result.stdout.strip().splitlines():
        video_id = line.strip()
        if video_id and video_id not in seen:
            seen.add(video_id)
            urls.append(f"https://www.youtube.com/watch?v={video_id}")
    return urls

