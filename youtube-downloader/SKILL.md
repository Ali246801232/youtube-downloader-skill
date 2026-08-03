---
name: youtube-downloader
description: Download videos, audios, subtitles, and transcripts from YouTube videos and playlists using yt-dlp. Use when the user provides a YouTube video or playlist URL, asks to download videos, or when the conversation involves YouTube URLs.
license: MIT License. ../LICENSE has complete term
compatibility: Requires Python 3.10+, yt-dlp, and FFmpeg.
---

# yt-dlp Video Downloader Skill

This skill provides tools for downloading videos and extracting audio from various platforms using yt-dlp.


## Features

- Download videos, audio, subtitles, and transcripts from YouTube
- Bulk download from multiple videos in parallel
- Auto-detect video URLs from text, files, or playlists.
- Support for different quality settings and file formats


## Prerequisites

When using the skill for the first time, before using any other workflow or command, you **MUST** run the following command:
```
python scripts/yt.py test-deps
```

This will output if all dependencies are installed. Otherwise, it will output which ones are missing and how to install them. If all dependencies are present, continue using the skill. Otherwise, inform the user which dependencies are missing, and ask if they would like to install them. If they confirm that they would, use the commands provided by `test-deps` to do so. Otherwise, do not install the dependencies and do not use the skill.


## Workflows

For concrete examples of usage for the commands mentioned in each workflow, refer to [references/examples.md](./references/examples.md). You can also run `--help` for any subcommand.


### Getting metadata

Use this when you need the metadata of a video, playlist or channel, or a specific field from it.

Command:
```
python scripts/yt.py info <url> [options]
```
Options:
- `--field`: Specifc field to output instead of entire metadata: `title`, `description`, `duration`, etc.
- `--output-file`: File to write output to instead of stdout


### Downloading videos

Use this when you need to download YouTube video.

Command:
```
python scripts/yt.py video <urls> [options]
```

Options:
- `--file-format`: Video file format: `mp4`, `webm`, `mkv`, etc. (default: `mp4`)
- `--quality`: Video quality (resolution): `best`, `720p`, `1080p`, `4k`, etc. (default: `best`)
- `--outout-dir`: Output directory (default: `.`)


### Downloading audio

Use this when you need to download the audio of a YouTube video.

Command:
```
python scripts/yt.py audio <urls> [options]
```

Options:
- `--file-format`: Audio file format: `mp3`, `m4a`, `wav`, etc. (default: `mp3`)
- `--quality`: Audio quality (bitrate): `best`, `128K`, `192K`, `256K`, `320K`, etc. (default: `best`)
- `--outout-dir`: `--outout-dir`: Output directory (default: `.`)


### Downloading subtitles

Use this when you need to download the subtitles of a YouTube video.

Command:
```
python scripts/yt.py subtitles <urls> [options]
```

Options:
- `--file-format`: Subtitles file format: `srt`, `vtt`, `ttml`, etc. (default: `srt`)
- `--language`: Language code: `en`, `en-GB`, `ja`, etc. (default: auto-detect primary language from video)
- `--outout-dir`: `--outout-dir`: Output directory (default: `.`)


### Downloading transcripts

Use this when you need to download the plain-text transcript of a YouTube video.

Command:
```
python scripts/yt.py transcript <urls> [options]
```

Options:
- `--language`: Language code: `en`, `en-GB`, `ja`, etc. (default: auto-detect primary language from video)
- `--outout-dir`: `--outout-dir`: Output directory (default: `.`)


### Downloading in bulk

Use this when you need to download videos, audio, subtitles, or transcripts for multiple videos at once.

Every download command (`video`, `audio`, `subtitles`, `transcript`) accepts multiple URL sources as positional arguments. Each argument is processed as follows:
- **Video URL** (`youtube.com/watch?v=...`, `youtu.be/...`):
  Used directly.
- **Playlist URL** (`youtube.com/playlist?list=...`):
  Expanded to include all individual video URLs.
- **File path** (e.g. `urls.txt`):
  Scanned for any YouTube video URLs in the file's text content.
- **Anything else**:
  Scanned as text for any YouTube video URLs.

Each of these commands also supports a `--max-workers` option (default: `5`) to control how many downloads can be done in parallel at once.

Results are reported per-URL once all downloads are complete:
```
[DONE]  {url}  saved to    {filepath}
[ERROR] {url}  with error  {error}
...
```
