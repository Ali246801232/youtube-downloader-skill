#!/usr/bin/env python3
"""Test that the dependencies required for the skill are present."""

import subprocess


def test_yt_dlp_installed():
    """Check if yt-dlp is installed."""
    try:
        result = subprocess.run(["yt-dlp", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"[OK]    yt-dlp is installed: version {version}")
            return True
        else:
            print("[ERROR] yt-dlp --version failed")
            return False
    except FileNotFoundError:
        print("[ERROR] yt-dlp is not installed")
        print("        Install with: `pip install yt-dlp` or `uv tool install yt-dlp`")
        return False


def test_ffmpeg_installed():
    """Check if ffmpeg is installed."""
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.split("\n")[0].split("ffmpeg version ")[1].split(" ")[0]
            print(f"[OK]    ffmpeg is installed: version {version}")
            return True
        else:
            print("[ERROR] ffmpeg -version failed")
            return False
    except FileNotFoundError:
        print("[ERROR] ffmpeg is not installed (required for format conversion)")
        print("        Install with: `winget install ffmpeg` (Windows), `brew install ffmpeg` (macOS), or `apt install ffmpeg` (Linux)")
        return False


def test_deps():
    yt_dlp_ok = test_yt_dlp_installed()
    ffmpeg_ok = test_ffmpeg_installed()

    if yt_dlp_ok and ffmpeg_ok:
        print("[OK]    Dependencies look good!")
        print("        The skill is ready to use")
    else:
        print("[ERROR] Please install missing dependencies before using the skill.")
