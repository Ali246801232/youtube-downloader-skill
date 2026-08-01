#!/usr/bin/env python3
"""Extract YouTube video URLs from text string, a file, or a playlist."""

import re
import subprocess
from pathlib import Path
from typing import Literal, overload


_VIDEO_URL_PATTERN = re.compile(
    r"(?:https?:\/\/)?"                  # https://, http://
    r"(?:"                               # 
        r"(?:www\.|m\.)?youtube\.com\/"  #     www.youtube.com/, m.youtube.com/
        r"(?:"                           # 
            r"watch\?(?:[^&\s]*&)*?v="   #         watch?v=, watch?[other query parameters]&v=
            r"|"                         #         |
            r"shorts\/"                  #         shorts/
            r"|"                         #         |
            r"v\/"                       #         v/
        r")"                             # 
        r"|"                             #     |
        r"youtu\.be\/"                   #     youtu.be/
    r")"                                 # 
    r"([a-zA-Z0-9_-]{11})"               # (capturing group 1: video ID)
    r"(?:[?&]\S*)?"                      # other query parameters
    , re.IGNORECASE
)

_PLAYLIST_URL_PATTERN = re.compile(
    r"(?:https?:\/\/)?"               # https://, http://
    r"(?:www\.|m\.)?youtube\.com\/"   # www.youtube.com/, m.youtube.com/
    r"playlist\?(?:[^&\s]*&)*?list="  # playlist?list=, playlist?[other query parameters]&list=
    r"([a-zA-Z0-9_-]+)"               # (capturing group 1: playlist ID)
    r"(?:[?&]\S*)?"                   # other query parameters
    , re.IGNORECASE
)

_CHANNEL_URL_PATTERN = re.compile(
    r"(?:https?:\/\/)?"              # https://, http://
    r"(?:www\.|m\.)?youtube\.com\/"  # www.youtube.com/, m.youtube.com/
    r"("                             # ( capturing group 1:
        r"@[^?&\s\/]+"               #     @handle
        r"|"                         #     |
        r"channel\/[^?&\s\/]+"       #     channel/channel-ID
        r"|"                         #     |
        r"c\/[^?&\s\/]+"             #     c/custom-url
        r"|"                         #     |
        r"user\/[^?&\s\/]+"          #     user/username
    r")"                             # )
    r"(?:\/[^?&\s\/]+\/?)?"          # subsections (/featured/, /videos/, etc.)
    r"(?:^[\/?&\s]*)?"               # other query parameters
    , re.IGNORECASE
)


def _finder(pattern: re.Pattern, template: str):
    @overload
    def find_urls(text: str, fullmatch: Literal[True]) -> str: ...
    
    @overload
    def find_urls(text: str, fullmatch: Literal[False] = False) -> list[str]: ...
    
    def find_urls(text: str, fullmatch: bool = False) -> str|list[str]:
        text = text.strip()
        if fullmatch:
            match = pattern.fullmatch(text)
            return template.format(match.group(1)) if match else None
        
        matches = pattern.finditer(text)
        urls = [template.format(m.group(1)) for m in matches]
        return list(dict.fromkeys(urls))
        
    return find_urls

find_video_urls = _finder(_VIDEO_URL_PATTERN, "https://www.youtube.com/watch?v={}")
find_playlist_urls = _finder(_PLAYLIST_URL_PATTERN, "https://www.youtube.com/playlist?list={}")
find_channel_urls = _finder(_CHANNEL_URL_PATTERN, "https://www.youtube.com/{}/about")


def extract_urls_from_text(text: str, expand_playlists: bool = False) -> list[str]:
    """Return a list of YouTube video URLs in a text string, optionally find and extract from playlist URLs as well."""
    video_urls = find_video_urls(text)
    if expand_playlists:
        playlist_urls = find_playlist_urls(text)
        video_urls += [extract_urls_from_playlist(playlist_url) for playlist_url in playlist_urls]
        video_urls = list(dict.fromkeys(video_urls))
    return video_urls


def extract_urls_from_file(file_path: str|Path, expand_playlists: bool = False) -> list[str]:
    """Return a list of YouTube video URLs in a file, optionally find and extract from playlist URLs as well."""
    file_path = Path(file_path)
    if not(file_path.exists() and file_path.is_file()):
        raise RuntimeError(f"No file found at {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return extract_urls_from_text(file.read(), expand_playlists=expand_playlists)
    except Exception as e:
        raise RuntimeError(f"Error extracting URLs from file {file_path}: {e}")


def extract_urls_from_playlist(playlist_url: str) -> list[str]:
    """Return a list of YouTube video URLs in a playlist using yt-dlp."""
    if not (url := find_playlist_urls(playlist_url, fullmatch=True)):
        raise ValueError(f"Invalid playlist URL: {playlist_url}")

    try:
        result = subprocess.run(
            ["yt-dlp", "--flat-playlist", "--print", "url", url],
            capture_output=True, text=True, check=True
        )
    except FileNotFoundError as e:
        raise RuntimeError("yt-dlp is not installed") from e
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error fetching playlist from {playlist_url} using yt-dlp: {e.stderr.strip() or e.stdout.strip()}") from e

    return find_video_urls(result.stdout)
