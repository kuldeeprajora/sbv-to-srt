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
- A Python installation with Tcl/Tk (`tkinter`) 8.6 or newer is required only for the desktop interface

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

### macOS

Do not launch the GUI with Apple's `/usr/bin/python3`; its deprecated Tk 8.5 can produce a blank window on modern macOS.

For a Homebrew Python 3.14 installation, add the matching modern Tk package:

```bash
brew install python-tk@3.14
python3 sbv_to_srt_gui.py
```

For another Python version, install its matching `python-tk@3.x` formula. You can verify the active runtime with:

```bash
python3 -c "import tkinter as tk; print(tk.TkVersion)"
```

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

The conversion engine and desktop interface are covered by automated tests on macOS and Windows. Tagged releases build separate standalone artifacts for each platform, so end users do not need to install Python.

## Standalone Builds

The GitHub Actions release workflow creates:

- `SBV-to-SRT-macOS.zip` containing the macOS `.app`
- `SBV-to-SRT.exe` for Windows

Builds are unsigned during private development. macOS Gatekeeper or Windows SmartScreen may therefore display a warning until code signing is configured for a public release.
