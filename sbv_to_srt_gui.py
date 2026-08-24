#!/usr/bin/env python3
"""Desktop interface for the SBV to SRT converter."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Iterable

from sbv_to_srt import SBVConversionError, convert_file

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
except ImportError:
    tk = None
    filedialog = None
    messagebox = None
    ttk = None


APP_TITLE = "SBV to SRT Converter"


def normalized_path(path: Path) -> str:
    """Return a stable key for de-duplicating paths across platforms."""
    return os.path.normcase(str(path.expanduser().resolve()))


def collect_sbv_files(folder: Path) -> list[Path]:
    """Collect SBV files directly inside a folder, without recursion."""
    return sorted(
        (path for path in folder.iterdir() if path.is_file() and path.suffix.lower() == ".sbv"),
        key=lambda path: path.name.lower(),
    )


def choose_unique_destination(destination: Path, reserved: set[str]) -> Path:
    """Avoid two inputs targeting the same output path in a batch."""
    candidate = destination
    counter = 2
    while normalized_path(candidate) in reserved:
        candidate = destination.with_name(f"{destination.stem}_{counter}{destination.suffix}")
        counter += 1
    reserved.add(normalized_path(candidate))
    return candidate


def open_folder(folder: Path) -> None:
    """Open a folder in the native file manager."""
    if sys.platform == "win32":
        os.startfile(str(folder))  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(folder)])
    else:
        subprocess.Popen(["xdg-open", str(folder)])


class ConverterApp:
    def __init__(self, root: "tk.Tk") -> None:
        self.root = root
        self.files: list[Path] = []
        self.item_paths: dict[str, Path] = {}
        self.output_mode = tk.StringVar(value="source")
        self.output_folder = tk.StringVar(value="")
        self.overwrite = tk.BooleanVar(value=False)
        self.summary = tk.StringVar(value="Add one or more SBV files to begin.")
        self.progress_value = tk.DoubleVar(value=0)
        self.last_output_folder: Path | None = None

        self._configure_window()
        self._configure_style()
        self._build_ui()
        self._bind_shortcuts()
        self._refresh_controls()

    def _configure_window(self) -> None:
        self.root.title(APP_TITLE)
        self.root.geometry("820x590")
        self.root.minsize(680, 480)
        self.root.option_add("*tearOff", False)

    def _configure_style(self) -> None:
        style = ttk.Style(self.root)
        available = style.theme_names()
        if sys.platform == "win32" and "vista" in available:
            style.theme_use("vista")
        elif "clam" in available and sys.platform != "darwin":
            style.theme_use("clam")
        style.configure("Title.TLabel", font=("TkDefaultFont", 20, "bold"))
        style.configure("Subtitle.TLabel", foreground="#60646c")
        style.configure("Primary.TButton", font=("TkDefaultFont", 10, "bold"), padding=(14, 8))

    def _build_ui(self) -> None:
        container = ttk.Frame(self.root, padding=20)
        container.grid(row=0, column=0, sticky="nsew")
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(2, weight=1)

        header = ttk.Frame(container)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="SBV to SRT", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            header,
            text="Convert YouTube SBV subtitles into standard SRT files.",
            style="Subtitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(3, 0))

        toolbar = ttk.Frame(container)
        toolbar.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        ttk.Button(toolbar, text="Add Files…", command=self.add_files).pack(side="left")
        ttk.Button(toolbar, text="Add Folder…", command=self.add_folder).pack(side="left", padx=(8, 0))
        self.remove_button = ttk.Button(toolbar, text="Remove Selected", command=self.remove_selected)
        self.remove_button.pack(side="left", padx=(18, 0))
        self.clear_button = ttk.Button(toolbar, text="Clear", command=self.clear_files)
        self.clear_button.pack(side="left", padx=(8, 0))

        list_frame = ttk.Frame(container)
        list_frame.grid(row=2, column=0, sticky="nsew")
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        self.file_list = ttk.Treeview(
            list_frame,
            columns=("folder", "status"),
            selectmode="extended",
            show="tree headings",
        )
        self.file_list.heading("#0", text="SBV file", anchor="w")
        self.file_list.heading("folder", text="Location", anchor="w")
        self.file_list.heading("status", text="Status", anchor="w")
        self.file_list.column("#0", width=210, minwidth=140)
        self.file_list.column("folder", width=390, minwidth=180)
        self.file_list.column("status", width=110, minwidth=90, stretch=False)
        self.file_list.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.file_list.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.file_list.configure(yscrollcommand=scrollbar.set)
        self.file_list.bind("<<TreeviewSelect>>", lambda _event: self._refresh_controls())

        output_frame = ttk.LabelFrame(container, text="Output", padding=12)
        output_frame.grid(row=3, column=0, sticky="ew", pady=(16, 0))
        output_frame.columnconfigure(1, weight=1)

        ttk.Radiobutton(
            output_frame,
            text="Save beside each source file",
            variable=self.output_mode,
            value="source",
            command=self._refresh_output_controls,
        ).grid(row=0, column=0, columnspan=3, sticky="w")
        ttk.Radiobutton(
            output_frame,
            text="Save all files in:",
            variable=self.output_mode,
            value="folder",
            command=self._refresh_output_controls,
        ).grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_folder)
        self.output_entry.grid(row=1, column=1, sticky="ew", padx=(10, 8), pady=(8, 0))
        self.browse_output_button = ttk.Button(output_frame, text="Browse…", command=self.choose_output_folder)
        self.browse_output_button.grid(row=1, column=2, pady=(8, 0))
        ttk.Checkbutton(
            output_frame,
            text="Replace existing SRT files",
            variable=self.overwrite,
        ).grid(row=2, column=0, columnspan=3, sticky="w", pady=(10, 0))

        footer = ttk.Frame(container)
        footer.grid(row=4, column=0, sticky="ew", pady=(16, 0))
        footer.columnconfigure(0, weight=1)
        ttk.Label(footer, textvariable=self.summary).grid(row=0, column=0, columnspan=2, sticky="w")
        self.progress = ttk.Progressbar(footer, variable=self.progress_value, maximum=100)
        self.progress.grid(row=1, column=0, sticky="ew", pady=(8, 0), padx=(0, 12))
        self.convert_button = ttk.Button(
            footer,
            text="Convert to SRT",
            style="Primary.TButton",
            command=self.convert_all,
        )
        self.convert_button.grid(row=1, column=1, sticky="e", pady=(8, 0))
        self.open_output_button = ttk.Button(footer, text="Open Output Folder", command=self.open_output)
        self.open_output_button.grid(row=2, column=1, sticky="e", pady=(8, 0))

    def _bind_shortcuts(self) -> None:
        self.root.bind("<Control-o>", lambda _event: self.add_files())
        self.root.bind("<Command-o>", lambda _event: self.add_files())
        self.root.bind("<Delete>", lambda _event: self.remove_selected())
        self.root.bind("<BackSpace>", lambda _event: self.remove_selected())

    def add_files(self) -> None:
        selected = filedialog.askopenfilenames(
            parent=self.root,
            title="Select SBV subtitle files",
            filetypes=(("SBV subtitle files", "*.sbv"), ("All files", "*.*")),
        )
        self._append_files(Path(path) for path in selected)

    def add_folder(self) -> None:
        selected = filedialog.askdirectory(parent=self.root, title="Select a folder containing SBV files")
        if not selected:
            return
        folder = Path(selected)
        try:
            files = collect_sbv_files(folder)
        except OSError as error:
            messagebox.showerror(APP_TITLE, f"Could not read the selected folder.\n\n{error}")
            return
        if not files:
            messagebox.showinfo(APP_TITLE, "No .sbv files were found directly inside that folder.")
            return
        self._append_files(files)

    def _append_files(self, paths: Iterable[Path]) -> None:
        existing = {normalized_path(path) for path in self.files}
        added = 0
        rejected = 0
        for path in paths:
            candidate = path.expanduser()
            if not candidate.is_file() or candidate.suffix.lower() != ".sbv":
                rejected += 1
                continue
            key = normalized_path(candidate)
            if key in existing:
                continue
            self.files.append(candidate.resolve())
            existing.add(key)
            added += 1
        self.files.sort(key=lambda path: (path.name.lower(), str(path.parent).lower()))
        self._rebuild_file_list()
        if rejected:
            messagebox.showwarning(APP_TITLE, f"Ignored {rejected} item(s) that were not valid SBV files.")
        if added:
            self.summary.set(f"{len(self.files)} SBV file(s) ready to convert.")

    def _rebuild_file_list(self) -> None:
        previous_status = {
            normalized_path(path): self.file_list.set(item_id, "status")
            for item_id, path in self.item_paths.items()
            if self.file_list.exists(item_id)
        }
        self.file_list.delete(*self.file_list.get_children())
        self.item_paths.clear()
        for index, path in enumerate(self.files):
            item_id = f"file-{index}"
            self.file_list.insert(
                "",
                "end",
                iid=item_id,
                text=path.name,
                values=(str(path.parent), previous_status.get(normalized_path(path), "Ready")),
            )
            self.item_paths[item_id] = path
        self._refresh_controls()

    def remove_selected(self) -> None:
        selected_keys = {
            normalized_path(self.item_paths[item_id])
            for item_id in self.file_list.selection()
            if item_id in self.item_paths
        }
        if not selected_keys:
            return
        self.files = [path for path in self.files if normalized_path(path) not in selected_keys]
        self._rebuild_file_list()
        self.summary.set(f"{len(self.files)} SBV file(s) ready to convert." if self.files else "Add one or more SBV files to begin.")

    def clear_files(self) -> None:
        self.files = []
        self.last_output_folder = None
        self.progress_value.set(0)
        self._rebuild_file_list()
        self.summary.set("Add one or more SBV files to begin.")

    def choose_output_folder(self) -> None:
        initial = self.output_folder.get() or (str(self.files[0].parent) if self.files else str(Path.home()))
        selected = filedialog.askdirectory(
            parent=self.root,
            title="Choose an output folder",
            initialdir=initial,
        )
        if selected:
            self.output_folder.set(selected)
            self.output_mode.set("folder")
            self._refresh_output_controls()

    def _refresh_output_controls(self) -> None:
        state = "normal" if self.output_mode.get() == "folder" else "disabled"
        self.output_entry.configure(state=state)
        self.browse_output_button.configure(state=state)

    def _refresh_controls(self) -> None:
        has_files = bool(self.files)
        self.remove_button.configure(state="normal" if self.file_list.selection() else "disabled")
        self.clear_button.configure(state="normal" if has_files else "disabled")
        self.convert_button.configure(state="normal" if has_files else "disabled")
        self.open_output_button.configure(state="normal" if self.last_output_folder else "disabled")
        self._refresh_output_controls()

    def _set_file_status(self, path: Path, status: str) -> None:
        key = normalized_path(path)
        for item_id, item_path in self.item_paths.items():
            if normalized_path(item_path) == key:
                self.file_list.set(item_id, "status", status)
                self.file_list.see(item_id)
                break

    def _resolve_output_folder(self) -> tuple[bool, Path | None]:
        if self.output_mode.get() == "source":
            return True, None
        raw_folder = self.output_folder.get().strip()
        if not raw_folder:
            messagebox.showwarning(APP_TITLE, "Choose an output folder before converting.")
            return False, None
        folder = Path(raw_folder).expanduser()
        try:
            folder.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            messagebox.showerror(APP_TITLE, f"Could not create the output folder.\n\n{error}")
            return False, None
        if not folder.is_dir():
            messagebox.showerror(APP_TITLE, "The selected output path is not a folder.")
            return False, None
        return True, folder.resolve()

    def convert_all(self) -> None:
        if not self.files:
            return
        output_is_valid, output_folder = self._resolve_output_folder()
        if not output_is_valid:
            return

        self.convert_button.configure(state="disabled")
        self.progress_value.set(0)
        self.summary.set("Converting…")
        self.root.update_idletasks()

        converted = 0
        skipped = 0
        failures: list[str] = []
        reserved: set[str] = set()

        for index, input_path in enumerate(self.files, start=1):
            base_destination = (
                output_folder / input_path.with_suffix(".srt").name
                if output_folder is not None
                else input_path.with_suffix(".srt")
            )
            destination = choose_unique_destination(base_destination, reserved)
            if destination.exists() and not self.overwrite.get():
                skipped += 1
                self._set_file_status(input_path, "Skipped")
                self.last_output_folder = destination.parent
            else:
                try:
                    convert_file(input_path, destination)
                    converted += 1
                    self._set_file_status(input_path, "Converted")
                    self.last_output_folder = destination.parent
                except (SBVConversionError, OSError, UnicodeError) as error:
                    failures.append(f"{input_path.name}: {error}")
                    self._set_file_status(input_path, "Error")
            self.progress_value.set(index / len(self.files) * 100)
            self.root.update_idletasks()

        parts = [f"Converted: {converted}", f"Skipped: {skipped}", f"Errors: {len(failures)}"]
        self.summary.set("  •  ".join(parts))
        self._refresh_controls()

        if failures:
            detail = "\n".join(failures[:8])
            if len(failures) > 8:
                detail += f"\n…and {len(failures) - 8} more error(s)."
            messagebox.showerror(APP_TITLE, f"Some files could not be converted.\n\n{detail}")
        elif converted:
            messagebox.showinfo(APP_TITLE, f"Successfully converted {converted} file(s).")
        elif skipped:
            messagebox.showinfo(
                APP_TITLE,
                "No files were changed because the SRT outputs already exist.\n\n"
                "Enable ‘Replace existing SRT files’ to overwrite them.",
            )

    def open_output(self) -> None:
        if not self.last_output_folder:
            return
        try:
            open_folder(self.last_output_folder)
        except OSError as error:
            messagebox.showerror(APP_TITLE, f"Could not open the output folder.\n\n{error}")


def main() -> int:
    if tk is None:
        print(
            "Error: tkinter is not available in this Python installation. "
            "Install a Python build that includes Tcl/Tk, then run this file again.",
            file=sys.stderr,
        )
        return 1

    root = tk.Tk()
    ConverterApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
