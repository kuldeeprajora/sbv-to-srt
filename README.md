# SBV to SRT

SBV to SRT is a dependency-free Python tool that converts YouTube-style `.sbv` subtitle files into standards-compliant `.srt` files. It includes both a desktop interface and a command-line interface.

## Features

- Convert one SBV file or multiple files in one command
- Convert every `.sbv` file directly inside a selected directory
- Add, remove, and review files in a desktop batch-conversion queue
- Save results beside each source or into one selected output folder
- Skip existing SRT files by default, with an optional replace setting in the desktop app
- Track per-file conversion status and open the output folder
- Preserve multiline subtitle text
- Read UTF-8 files with or without a byte-order mark
- Normalize timestamps to the SRT `HH:MM:SS,mmm` format
- Validate timing lines, timestamp ranges, subtitle text, and reversed start/end times
- Write UTF-8 SRT output with consistent line endings
- Prompt for an input path when the script is launched without arguments
- No third-party Python packages required

## Requirements

- Python 3.9 or newer
- macOS, Windows, or Linux
- A Python installation with Tcl/Tk (`tkinter`) is required only for the desktop interface

## Desktop Interface

Launch the app with:

```bash
python3 sbv_to_srt_gui.py
```

Then:

1. Use **Add Files** to select one or more `.sbv` files, or **Add Folder** to collect files from a folder.
2. Choose whether SRT files should be saved beside their sources or in one output folder.
3. Leave **Replace existing SRT files** disabled for safe, non-destructive conversion.
4. Click **Convert to SRT**.
5. Review the status shown for each file or click **Open Output Folder**.

Folder selection is non-recursive. If your Python reports that `tkinter` is unavailable, install a Python build that includes Tcl/Tk and launch the app with that interpreter.

## Command-Line Usage

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

The conversion engine and initial desktop interface are functional in local testing. This repository is private while the UI is validated on macOS and Windows and standalone app packaging is prepared.
