# Examples

All commands listed in this section are run from the skill directory (`youtube-downloader/`) as follows:
```
python scripts/yt.py <command> [options]
```


## Dependency check

```bash
python scripts/yt.py test-deps
```


## Getting metadata

Get a video's metadata:

```bash
python scripts/yt.py info "https://www.youtube.com/watch?v=ptnAeX39DFI"
```

Get a channel's metadata:

```bash
python scripts/yt.py info "https://www.youtube.com/@Animenzzz"
```

Get a playlist's metadata:

```bash
python scripts/yt.py info "https://www.youtube.com/playlist?list=PL3_NLXp9puXUXEpCuln7Rwdy5lO0QzViT"
```

Get a video's title:

```bash
python scripts/yt.py info "https://www.youtube.com/watch?v=ptnAeX39DFI" --field title
```

Get a video's available subtitle languages:

```bash
python scripts/yt.py info "https://www.youtube.com/watch?v=ptnAeX39DFI" --field subtitles
```

Get a channel's handle:
```bash
python scripts/yt.py info "y"
```

Save a video's metadata to a file:

```bash
python scripts/yt.py info "https://www.youtube.com/watch?v=ptnAeX39DFI" --output-file video-info.json
```


## Downloading videos

Download at best quality as MP4 (default):

```bash
python scripts/yt.py video "https://www.youtube.com/watch?v=ptnAeX39DFI"
```

Download at 1080p as MKV:

```bash
python scripts/yt.py video "https://www.youtube.com/watch?v=ptnAeX39DFI" --quality 1080p --file-format mkv
```

Download at 4K as WebM:

```bash
python scripts/yt.py video "https://www.youtube.com/watch?v=ptnAeX39DFI" --quality 4k --file-format webm
```

Download to a specific directory:

```bash
python scripts/yt.py video "https://www.youtube.com/watch?v=ptnAeX39DFI" --output-dir "~/Videos/YouTube"
```


## Downloading audio

Download at best quality as MP3 (default):

```bash
python scripts/yt.py audio "https://www.youtube.com/watch?v=ptnAeX39DFI"
```

Download at 320K as M4A:

```bash
python scripts/yt.py audio "https://www.youtube.com/watch?v=ptnAeX39DFI" --quality 320K --file-format m4a
```

Download to a specific directory:

```bash
python scripts/yt.py audio "https://www.youtube.com/watch?v=ptnAeX39DFI" --output-dir "~/Videos/YouTube"
```


## Downloading subtitles

Download subtitles in auto-detected language as SRT:

```bash
python scripts/yt.py subtitles "https://www.youtube.com/watch?v=ptnAeX39DFI"
```

Download Japanese subtitles:

```bash
python scripts/yt.py subtitles "https://www.youtube.com/watch?v=ptnAeX39DFI" --language ja
```

Download English (US) subtitles as VTT:

```bash
python scripts/yt.py subtitles "https://www.youtube.com/watch?v=ptnAeX39DFI" --language en --file-format vtt
```


## Downloading transcripts

Download plain-text transcript:

```bash
python scripts/yt.py transcript "https://www.youtube.com/watch?v=ptnAeX39DFI"
```

Download plain-text transcript in French:

```bash
python scripts/yt.py transcript "https://www.youtube.com/watch?v=ptnAeX39DFI" --language fr
```


## Downloading in bulk

Download MP4 videos from multiple URLs:

```bash
python scripts/yt.py video "https://www.youtube.com/watch?v=ptnAeX39DFI" "https://www.youtube.com/watch?v=0_W4BwfRvkg" --file-format mp4
```

Download 192K audio all videos from a playlist:
```bash
python scripts/yt.py audio "https://www.youtube.com/playlist?list=PL3_NLXp9puXUXEpCuln7Rwdy5lO0QzViT" --quality 192K
```

Download SRT subtitles from a text file containing URLs:

```bash
python scripts/yt.py subtitles "urls.txt" --file-format srt
```

Download English transcripts of all videos from text containing URLs:

```bash
python scripts/yt.py transcript "Check out https://youtu.be/0_W4BwfRvkg and also https://youtu.be/ptnAeX39DFI." --language en
```

Download videos from multiple sources:

```bash
python scripts/yt.py video "https://www.youtube.com/watch?v=ptnAeX39DFI" "https://www.youtube.com/watch?v=0_W4BwfRvkg" "urls.txt" "https://www.youtube.com/playlist?list=PL3_NLXp9puXUXEpCuln7Rwdy5lO0QzViT" "This is text with a URL: https://youtu.be/ptnAeX39DFI."
```
