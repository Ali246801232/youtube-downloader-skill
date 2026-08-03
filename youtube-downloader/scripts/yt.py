#!/usr/bin/env python3
"""Entry point to use the skill's scripts."""

import sys
import json
import argparse
from pathlib import Path
from collections.abc import Callable

from downloader import get_info, download_video, download_audio, download_subtitles, download_transcript
from extract_urls import find_video_urls, find_playlist_urls, extract_urls_from_playlist, extract_urls_from_file, extract_urls_from_text
from parallel_download import parallel_download, Result
from test_deps import test_deps


def _collect_video_urls(args: list[str], expand_playlists: bool = False) -> list[str]:
    urls = []
    for arg in args:
        path = Path(arg)
        if url := find_video_urls(arg, fullmatch=True):
            urls.append(url)
        elif url := find_playlist_urls(arg, fullmatch=True):
            urls.extend(extract_urls_from_playlist(url))
        elif path.exists() and path.is_file():
            urls.extend(extract_urls_from_file(path, expand_playlists=expand_playlists))
        else:
            urls.extend(extract_urls_from_text(arg, expand_playlists=expand_playlists))
    urls = list(dict.fromkeys(urls))
    return urls


def _report_results(results: list[Result]):
    for result in results:
        if result.success:
            print(f"[DONE]  {result.url}  saved to    {result.filepath}")
        else:
            print(f"[ERROR] {result.url}  with error  {result.error}", file=sys.stderr)


def _add_common_download_args(parser: argparse.ArgumentParser):
    parser.add_argument("urls", nargs="+", help="Video URLs, playlist URLs, or file paths to extract URLs from")
    parser.add_argument("--output-dir", "-o", default=".", help="Output directory")
    parser.add_argument("--expand-playlists", action="store_true", help="Expand playlist URLs found inside text or files; standalone playlist URL arguments are unaffected and expaned regardless")
    parser.add_argument("--max-workers", default=5, help="Maximum number of downloads in parallel at once")


def cmd_test_deps(_args):
    try:
        test_deps()
    except Exception as e:
        print(f"Error while testing dependencies: {e}")
        return 1


def cmd_info(args):
    """Output a YouTube URL's metadata as JSON or a specific field from it."""
    try:
        info = get_info(args.url)
    except Exception as e:
        print(f"Error while getting info for url {args.url}: {e}")
        return 1

    if args.field:
        if args.field not in info:
            print(f"No field named {args.field} in info")
            return
        text = info[args.field]
    else:
        text = json.dumps(info, indent=2)

    if args.output_file:
        args.output_file.parent.mkdir(parents=True, exist_ok=True)
        args.output_file.write_text(text, encoding="utf-8")
    else:
        print(text)


def cmd_download(args, download_func: Callable):
    """Use download_func on multiple YouTube URLs in parallel."""
    try:
        urls = _collect_video_urls(args.urls, args.expand_playlists)
        if not urls:
            print("No URLs found in given arguments")
            return

        print(f"Found {len(urls)} unique URLS, starting parallel download")

        Path(args.output_dir).mkdir(parents=True, exist_ok=True)
        kwargs = {
            k: v for k, v in vars(args).items()
            if k not in ("urls", "command", "expand_playlists", "max_workers") and v is not None
        }
        results = parallel_download(urls, lambda url: download_func(url, **kwargs), max_workers=args.max_workers)
        _report_results(results)
        if any(not result.success for result in results):
            return 1
    except Exception as e:
        print(f"Error while running parallel downloads: {e}", file=sys.stderr)
        return 1


def main():
    parser = argparse.ArgumentParser(description="YouTube Downloader Skill")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p = subparsers.add_parser("test-deps", help="Check if yt-dlp and ffmpeg are installed", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    p = subparsers.add_parser("info", help="Output the YouTube URL metadata as JSON or a specific field from it", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument("url", help="YouTube video, playlist, or channel URL")
    p.add_argument("--field", help="Specifc field to output instead of entire metadata: title, description, duration, etc.")
    p.add_argument("--output-file", "-o", help="File to write output to instead of stdout")

    p = subparsers.add_parser("video", help="Download one or more YouTube videos in parallel", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    _add_common_download_args(p)
    p.add_argument("--file-format", "-f", default="mp4", help="Video file format: mp4, webm, mkv, etc.")
    p.add_argument("--quality", "-q", default="best", help="Video quality (resolution): best, 720p, 1080p, 4k, etc.")

    p = subparsers.add_parser("audio", help="Download audio from one or more YouTube videos in parallel", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    _add_common_download_args(p)
    p.add_argument("--file-format", "-f", default="mp3", help="Audio file format: mp3, m4a, wav, etc.")
    p.add_argument("--quality", "-q", default="best", help="Audio quality (bitrate): best, 128K, 192K, 256K, 320K, etc.")

    p = subparsers.add_parser("subtitles", help="Download subtitles from one or more YouTube videos in parallel", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    _add_common_download_args(p)
    p.add_argument("--file-format", "-f", default="srt", help="Subtitles file format: srt, vtt, ttml, etc.")
    p.add_argument("--language", "-l", default=argparse.SUPPRESS, help="Language code: en, en.GB, ja, etc. (default: auto-detect primary language from video)")

    p = subparsers.add_parser("transcript", help="Download plain-text transcripts for one or more YouTube videos in parallel", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    _add_common_download_args(p)
    p.add_argument("--language", "-l", default=argparse.SUPPRESS, help="Language code: en, en.GB, ja, etc. (default: auto-detect primary language from video)")

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
