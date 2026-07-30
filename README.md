# YouTube Downloader Skill

An AI agent skill for downloading videos, audio, subtitles, and transcripts from YouTube using `yt-dlp`.

## Features

- Download videos, audio, subtitles, and transcripts from YouTube
- Bulk download from multiple videos in parallel
- Auto-detect video URLs from text, files, or playlists.
- Support for different quality settings and file formats

## Project Structure

```
├── youtube-downloader/
│   ├── SKILL.md
│   ├── references/
│   │   └── examples.md           # Usage examples
│   └── scripts/
│       ├── yt.py                 # CLI entry point
│       ├── downloader.py         # Core functinoality
│       ├── parallel_download.py  # Parallel downloading & retry logic
│       ├── extract_urls.py       # Extract YouTube video URLs
│       └── test_deps.py          # Verify dependencies
├── LICENSE
└── README.md
```

## Prerequisites

- **[Python 3](https://www.python.org/):** install from [python.org/downloads](https://www.python.org/downloads/)
- **[yt-dlp](https://github.com/yt-dlp/yt-dlp):** install with `pip install yt-dlp`
- **[ffmpeg](https://www.ffmpeg.org/):** install with:
    - Windows: `winget install ffmpeg`
    - macOS: `brew install ffmpeg`
    - Linux: `apt install ffmpeg`
