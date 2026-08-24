# SBV to SRT

SBV to SRT is a dependency-free Python command-line tool that converts YouTube-style `.sbv` subtitle files into standards-compliant `.srt` files.

## Features

- Convert one SBV file or multiple files in one command
- Convert every `.sbv` file directly inside a selected directory
- Preserve multiline subtitle text
- Read UTF-8 files with or without a byte-order mark
- Normalize timestamps to the SRT `HH:MM:SS,mmm` format
- Validate timing lines, timestamp ranges, subtitle text, and reversed start/end times
- Write UTF-8 SRT output with consistent line endings
- Prompt for an input path when the script is launched without arguments
- No third-party Python packages required

## Requirements

- Python 3.10 or newer
- macOS, Windows, or Linux

## Usage

Convert one file beside the original:

```bash
python3 sbv_to_srt.py subtitles.sbv
```

Choose an output filename:

```bash
python3 sbv_to_srt.py subtitles.sbv --output converted.srt
```

Convert several files into an output directory:

```bash
python3 sbv_to_srt.py first.sbv second.sbv --output converted
```

Convert all `.sbv` files directly inside a directory:

```bash
python3 sbv_to_srt.py path/to/subtitles --output converted
```

Run interactively:

```bash
python3 sbv_to_srt.py
```

Display all command-line options:

```bash
python3 sbv_to_srt.py --help
```

Directory scanning is non-recursive. When `--output` is omitted, each `.srt` file is written beside its matching `.sbv` file.

## Status

The converter is functional in current testing. This repository is private while documentation, automated tests, packaging, and release details are prepared.

