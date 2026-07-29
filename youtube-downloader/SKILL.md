---
name: youtube-downloader
description: Download videos, audios, subtitles, and transcripts from YouTube videos and playlists using yt-dlp. Use when the user provides a YouTube video or playlist URL, asks to download videos, or when the conversation involves YouTube URLs.
---

# yt-dlp Video Downloader Skill

This skill provides tools for downloading videos and extracting audio from various platforms using yt-dlp.

## Features

- Download videos from YouTube
- Download audio from YouTube videos
- Download subtitles from YouTube videos
- Download transcripts from YouTube videos
- Auto-detect video URLs from text (e.g. conversation), file, or playlist.
- Support for different quality settings and formats

## Workflows

When using the skill for the first time, you must follow these instructions before any other workflow:

1. Run `yt.py test-deps`. This will output if all dependencies are present. Otherwise, which ones are missing and how to install them.
2. If all dependencies are present, continue using the skill.
3. If not, Inform the user which dependencies are missing, and ask if they would like to install them.
4. If they confirm that they would, use the commands provided by `test-deps` to do so.
5. If not, do not install the dependencies and do not use the skill.

### Displaying video information



### Downloading videos



### Downloading audios



### Downloading subtitles



### Downloading transcripts



### Downloading in bulk (i.e. multiple URLs or a playlist)



## Dependencies

- `yt-dlp`: Main video downloader
- `ffmpeg`: Audio/video processing (required for format conversion)
- `python3` with standard library

All scripts are self-contained and use only built-in Python modules.
