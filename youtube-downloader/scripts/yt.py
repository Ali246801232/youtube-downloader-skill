#!/usr/bin/env python3
"""Entry point to use the skill's scripts."""

import sys
import json
import argparse
from pathlib import Path
from collections.abc import Callable

from downloader import get_video_info, download_video, download_audio, download_subtitles, download_transcript
from extract_urls import is_video_url, is_playlist_url, extract_urls_from_playlist, extract_urls_from_file, extract_urls_from_text
from parallel_download import parallel_download, Result
from test_deps import test_deps


def _collect_urls(args: list[str]) -> list[str]:
    urls = []
    for arg in args:
        path = Path(arg)
        if is_video_url(arg):
            urls.append(arg)
        elif is_playlist_url(arg):
            urls.extend(extract_urls_from_playlist(arg))
        elif path.exists() and path.is_file():
            urls.extend(extract_urls_from_file(path))
        else:
            urls.extend(extract_urls_from_text(arg))
    seen = set()
    unique = []
    for url in urls:
        if url not in seen:
            seen.add(url)
            unique.append(url)
    return unique


def _report_results(results: list[Result]):
    for result in results:
        if result.success:
            print(f"[DONE]  {result.url}  saved to    {result.filepath}")
        else:
            print(f"[ERROR] {result.url}  with error  {result.error}", file=sys.stderr)


def cmd_test_deps(_args):
    try:
        test_deps()
    except Exception as e:
        print(f"Error while testing dependencies: {e}")
        return 1


def cmd_info(args):
    """Output a video's metadata as JSON or a specific field from it."""
    if not is_video_url(args.url):
        print(f"{args.url} is not a valid YouTube video URL")
        return 1
    try:
        video_info = get_video_info(args.url)
    except Exception as e:
        print(f"Error while getting video info for url {args.url}: {e}")
        return 1
    if args.field:
        if args.field not in video_info:
            print(f"No field {args.field} in video info")
            return
        text = video_info[args.field]
    else:
        text = json.dumps(video_info, indent=2)
    if args.output_file:
        args.output_file.parent.mkdir(parents=True, exist_ok=True)
        args.output_file.write_text(text, encoding="utf-8")
    else:
        print(text)


def cmd_download(args, download_func: Callable):
    """Use download_func on multiple YouTube URLs in parallel."""
    try:
        urls = _collect_urls(args.urls)
        if not urls:
            print("No URLs found in given arguments")
            return
        print(f"Found {len(urls)} unique URLS, starting parallel download")
        Path(args.output_dir).mkdir(parents=True, exist_ok=True)
        kwargs = {
            k: v for k, v in vars(args).items()
            if k not in ("urls", "command") and v is not None
        }
        results = parallel_download(urls, lambda url: download_func(url, **kwargs))
        _report_results(results)
        if any(not result.success for result in results):
            return 1
    except Exception as e:
        print(f"Error while running parallel downloads: {e}", file=sys.stderr)
        return 1


def main():
    parser = argparse.ArgumentParser(description="YouTube Downloader Skill")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p = subparsers.add_parser("test-deps", help="Check if yt-dlp and ffmpeg are installed")

    p = subparsers.add_parser("info", help="Output the YouTube video metadata as JSON or a specific field from it")
    p.add_argument("url", help="YouTube video URL")
    p.add_argument("--field", help="Specifc field to output instead of entire metadata")
    p.add_argument("--output-file", "-o", help="File to write output to instead of stdout")

    p = subparsers.add_parser("video", help="Download one or more YouTube videos in parallel")
    p.add_argument("urls", nargs="+", help="Video URLs, playlist URLs, or file paths to extract URLs from")
    p.add_argument("--file-format", "-f", default="mp4", help="Video file format: mp4, webm, mkv, etc. (default: mp4)")
    p.add_argument("--quality", "-q", default="best", help="Video quality: best, 720p, 1080p, 4k, etc. (default: best)")
    p.add_argument("--language", "-l", help="Language code for audio stream if multiple: en, en.GB, jp, etc. (default: auto-detect primary/only from video)")
    p.add_argument("--output-dir", "-o", default=".", help="Output directory (default: .)")

    p = subparsers.add_parser("audio", help="Download audio from one or more YouTube videos in parallel")
    p.add_argument("urls", nargs="+", help="Video URLs, playlist URLs, or file paths to extract URLs from")
    p.add_argument("--file-format", "-f", default="mp3", help="Audio file format: mp3, m4a, wav, etc. (default: mp3)")
    p.add_argument("--quality", "-q", default="192K", help="Audio quality: 128K, 192K, 256K, 320K, best, etc. (default: 192K)")
    p.add_argument("--language", "-l", help="Language code for audio stream if multiple: en, en.GB, jp, etc. (default: auto-detect primary/only from video)")
    p.add_argument("--output-dir", "-o", default=".", help="Output directory (default: .)")

    p = subparsers.add_parser("subtitles", help="Download subtitles from one or more YouTube videos in parallel")
    p.add_argument("urls", nargs="+", help="Video URLs, playlist URLs, or file paths to extract URLs from")
    p.add_argument("--file-format", "-f", default="srt", help="Subtitles file format: srt, vtt, ttml, etc. (default: srt)")
    p.add_argument("--language", "-l", help="Language code: en, en.GB, jp, etc. (default: auto-detect from video)")
    p.add_argument("--output-dir", "-o", default=".", help="Output directory (default: .)")

    p = subparsers.add_parser("transcript", help="Download transcripts for one or more YouTube videos in parallel")
    p.add_argument("urls", nargs="+", help="Video URLs, playlist URLs, or file paths to extract URLs from")
    p.add_argument("--language", "-l", help="Language code: en, en.GB, jp, etc. (default: auto-detect from video)")
    p.add_argument("--output-dir", "-o", default=".", help="Output directory (default: .)")

    args = parser.parse_args()

    dispatch = {
        "test-deps": cmd_test_deps,
        "info": cmd_info,
        "video": lambda args: cmd_download(args, download_video),
        "audio": lambda args: cmd_download(args, download_audio),
        "subtitles": lambda args: cmd_download(args, download_subtitles),
        "transcript": lambda args: cmd_download(args, download_transcript),
    }
    exit_code = dispatch[args.command](args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
