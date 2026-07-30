# Examples

All commands listed in this section are run from the skill directory (`youtube-downloader/`) as follows:
```
python scripts/yt.py <command> [options]
```

## Dependency check

```bash
python scripts/yt.py test-deps
```


## Displaying video information

Get full metadata as JSON:

```bash
python scripts/yt.py info "https://www.youtube.com/watch?v=6glHD1iMR_w"
```

Get just the title:

```bash
python scripts/yt.py info "https://www.youtube.com/watch?v=6glHD1iMR_w" --field title
```

Check available subtitle languages:

```bash
python scripts/yt.py info "https://www.youtube.com/watch?v=6glHD1iMR_w" --field subtitles
```


Save full metadata to a file:

```bash
python scripts/yt.py info "https://www.youtube.com/watch?v=6glHD1iMR_w" --output-file video-info.json
```


## Downloading videos

Download at best quality as MP4 (default):

```bash
python scripts/yt.py video "https://www.youtube.com/watch?v=6glHD1iMR_w"
```

Download at 1080p as MKV:

```bash
python scripts/yt.py video "https://www.youtube.com/watch?v=6glHD1iMR_w" --quality 1080p --file-format mkv
```

Download at 4K as WebM:

```bash
python scripts/yt.py video "https://www.youtube.com/watch?v=6glHD1iMR_w" --quality 4k --file-format webm
```

Download to a specific directory:

```bash
python scripts/yt.py video "https://www.youtube.com/watch?v=6glHD1iMR_w" --output-dir "~/Videos/YouTube"
```


## Downloading audio

Download at best quality as MP3 (default):

```bash
python scripts/yt.py audio "https://www.youtube.com/watch?v=6glHD1iMR_w"
```

Download at 320K as M4A:

```bash
python scripts/yt.py audio "https://www.youtube.com/watch?v=6glHD1iMR_w" --quality 320K --file-format m4a
```

Download to a specific directory:

```bash
python scripts/yt.py audio "https://www.youtube.com/watch?v=6glHD1iMR_w" --output-dir "~/Videos/YouTube"
```


## Downloading subtitles

Download subtitles in auto-detected language as SRT:

```bash
python scripts/yt.py subtitles "https://www.youtube.com/watch?v=6glHD1iMR_w"
```

Download Japanese subtitles:

```bash
python scripts/yt.py subtitles "https://www.youtube.com/watch?v=6glHD1iMR_w" --language jp
```

Download English (UK) subtitles as VTT:

```bash
python scripts/yt.py subtitles "https://www.youtube.com/watch?v=6glHD1iMR_w" --language en.GB --file-format vtt
```


## Downloading transcripts

Download plain-text transcript:

```bash
python scripts/yt.py transcript "https://www.youtube.com/watch?v=6glHD1iMR_w"
```

Download plain-text transcript in French:

```bash
python scripts/yt.py transcript "https://www.youtube.com/watch?v=6glHD1iMR_w" --language fr
```


## Downloading in bulk

Download videos from multiple URLs:

```bash
python scripts/yt.py video "https://www.youtube.com/watch?v=6glHD1iMR_w" "https://www.youtube.com/watch?v=9bZkp7q19f0" --file-format mp4
```

Download audio all videos from text containing URLs:

```bash
python scripts/yt.py audio "Check out https://youtu.be/6glHD1iMR_w and also https://youtu.be/1X8Jqn_TMzs." --quality 192K
```

Download subtitles from a text file containing URLs:

```bash
python scripts/yt.py subtitles "urls.txt" --file-format mp4
```

Download transcripts of all videos from a playlist:

```bash
python scripts/yt.py transcript "https://www.youtube.com/playlist?list=PL3_NLXp9puXWs19A9mdPXkoQ_WZ4IEBvp" --language en
```

Download videos from multiple sources:

```bash
python scripts/yt.py video "https://www.youtube.com/watch?v=6glHD1iMR_w" "https://www.youtube.com/watch?v=9bZkp7q19f0" "urls.txt" "https://www.youtube.com/playlist?list=PL3_NLXp9puXWs19A9mdPXkoQ_WZ4IEBvp" "This is text with a URL: https://youtu.be/6glHD1iMR_w."
```
