#!/usr/bin/env python3
"""Test that the dependencies required for the skill are present."""

import sys
import subprocess


REQUIRED_PYTHON = (3, 10)
def test_python_version():
    f"""Check if Python version meets requirement."""
    current = sys.version_info[:3]
    version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if current >= REQUIRED_PYTHON:
        print(f"[OK]    Python meets requirement: version {version}")
        return True
    else:
        print(f"[ERROR] Python is too old: {version} < {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]}+")
        print(f"        Install from: https://www.python.org/downloads/")
        return False


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
        print("[ERROR] ffmpeg is not installed")
        print("        Install with: `winget install ffmpeg` (Windows), `brew install ffmpeg` (macOS), or `apt install ffmpeg` (Linux)")
        return False


def test_deps():
    python_ok = test_python_version()
    yt_dlp_ok = test_yt_dlp_installed()
    ffmpeg_ok = test_ffmpeg_installed()

    if python_ok and yt_dlp_ok and ffmpeg_ok:
        print("[OK]    Dependencies look good!")
        print("        The skill is ready to use")
    else:
        print("[ERROR] Please install or update the required dependencies before using the skill.")
