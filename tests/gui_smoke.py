"""Construct the desktop UI without entering its event loop."""

import sys
import tkinter as tk
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sbv_to_srt import VERSION
from sbv_to_srt_gui import APP_TITLE, ConverterApp


root = tk.Tk()
root.withdraw()
app = ConverterApp(root)
root.update_idletasks()

assert root.title() == f"{APP_TITLE} {VERSION}"
assert app.file_list.winfo_exists()
assert app.convert_button.instate(["disabled"])
assert app.output_mode.get() == "source"

root.destroy()
print(f"GUI smoke test passed with Tk {tk.TkVersion}")
