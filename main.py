import io
import os
import sys
import urllib.request
import webbrowser
import traceback
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from pymem import Pymem
from pymem.process import module_from_name
from PIL import Image, ImageTk
import psutil
import logging

PROCESS_NAME = "HillClimbRacing.exe"
ADDR_COINS = "HillClimbRacing.exe+28CAD4"
ADDR_GEMS  = "HillClimbRacing.exe+28CAEC"
MAX_INT_32 = 2147483647
GITHUB_URL = "https://github.com/vihaanvp/Hill-Climb-Racing-Hacks"

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and PyInstaller onefile bundle."""
    if getattr(sys, "frozen", False):
        base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def parse_module_plus_offset(pm, s):
    mod_name, off_str = s.split('+', 1)
    off_str = off_str.strip().lower()
    offset = int(off_str, 16) if off_str.startswith("0x") or any(c in off_str for c in "abcdef") else int(off_str, 10)
    module = module_from_name(pm.process_handle, mod_name.strip())
    if not module:
        raise ValueError(f"Module '{mod_name}' not found.")
    return module.lpBaseOfDll + offset

def fetch_logo_image(local_png="assets/logo.png"):
    """Loads assets/logo.png as a Tkinter-compatible PhotoImage."""
    try:
        logo_path = resource_path(local_png)
        if os.path.exists(logo_path):
            img = Image.open(logo_path).convert("RGBA").resize((64, 64), Image.LANCZOS)
            return ImageTk.PhotoImage(img)
    except Exception:
        logging.debug("Local PNG logo load failed", exc_info=True)
    return None

def is_process_running(name):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == name:
            return True
    return False

def attach():
    if not is_process_running(PROCESS_NAME):
        messagebox.showwarning(
            "Process not found",
            f"'{PROCESS_NAME}' not running.\nPlease open the game and try again."
        )
        logging.warning(f"{PROCESS_NAME} is not running.")
        return None, None, None
    try:
        pm = Pymem(PROCESS_NAME)
        coin_addr = parse_module_plus_offset(pm, ADDR_COINS)
        gem_addr = parse_module_plus_offset(pm, ADDR_GEMS)
        logging.info(f"Attached to {PROCESS_NAME}.")
        return pm, coin_addr, gem_addr
    except Exception as e:
        logging.error(f"Failed to attach: {e}")
        messagebox.showerror(
            "Attachment failed",
            f"Could not attach to {PROCESS_NAME}.\nMake sure the game is running.\nError:\n{e}"
        )
        return None, None, None

def read_current_values():
    try:
        pm, coin_addr, gem_addr = attach()
        if pm is None: return
        coins = pm.read_int(coin_addr)
        gems = pm.read_int(gem_addr)
        pm.close_process()
        logging.info(f"Read values - Coins: {coins}, Gems: {gems}")
        entry_coins.delete(0, "end")
        entry_coins.insert(0, str(coins))
        entry_gems.delete(0, "end")
        entry_gems.insert(0, str(gems))
    except Exception as e:
        logging.error(f"Error reading values: {e}")
        messagebox.showwarning(
            "Read failed",
            f"Could not read game values.\nMake sure the game is running.\nError: {e}"
        )

def set_values():
    try:
        coin_text = entry_coins.get().strip()
        gem_text = entry_gems.get().strip()
        try:
            coins_val = int(coin_text, 0)
            gems_val = int(gem_text, 0)
        except ValueError:
            messagebox.showerror("Input error", "Values must be integers.")
            logging.warning(f"Invalid input - Coins: {coin_text}, Gems: {gem_text}")
            return

        pm, coin_addr, gem_addr = attach()
        if pm is None: return

        pm.write_int(coin_addr, coins_val)
        pm.write_int(gem_addr, gems_val)
        read_coins = pm.read_int(coin_addr)
        read_gems = pm.read_int(gem_addr)
        pm.close_process()

        entry_coins.delete(0, "end")
        entry_coins.insert(0, str(read_coins))
        entry_gems.delete(0, "end")
        entry_gems.insert(0, str(read_gems))

        logging.info(f"Values updated - Coins: {read_coins}, Gems: {read_gems}")
        messagebox.showinfo("Success", f"Updated!\nCoins: {read_coins}\nGems: {read_gems}")
    except Exception as e:
        tb = traceback.format_exc()
        logging.error(f"Failed to set values: {e}\n{tb}")
        messagebox.showerror(
            "Error",
            f"Could not set values.\nMake sure the game is running.\nError: {e}\n\nDetails:\n{tb}"
        )

def set_max(entry_widget):
    entry_widget.delete(0, "end")
    entry_widget.insert(0, str(MAX_INT_32))

def open_github(event=None):
    webbrowser.open_new(GITHUB_URL)

# --- GUI ---
app = ttk.Window(title="Hill Climb Racing Hack Menu", themename="cosmo", size=(650, 300), resizable=(False, False))

# Use assets/logo.png for window/taskbar icon and a logo label inside the GUI.
icon_image = fetch_logo_image("assets/logo.png")
if icon_image:
    app.iconphoto(True, icon_image)
    app.icon_img = icon_image  # Prevent garbage collection

    # Show logo in the GUI as well (optional)
    logo_label = ttk.Label(app, image=icon_image)
    logo_label.pack(pady=(10, 0))
else:
    logo_label = ttk.Label(app, text="[Logo not found]")
    logo_label.pack(pady=(10, 0))

ttk.Label(app, text="Hill Climb Racing Hack Menu", font=("Segoe UI", 12, "bold")).pack(pady=(8, 10))

mid = ttk.Frame(app)
mid.pack(pady=10)

coin_frame = ttk.Frame(mid)
coin_frame.grid(row=0, column=0, padx=20)
ttk.Label(coin_frame, text="💰 Coin Amount:", font=("Segoe UI", 10)).pack(anchor="w")

entry_coins = ttk.Entry(coin_frame, bootstyle=INFO, font=("Segoe UI", 11), width=18, justify="center")
entry_coins.pack(side="left", pady=(4, 6), padx=(0, 4))
ttk.Button(coin_frame, text="MAX", bootstyle=DANGER, command=lambda: set_max(entry_coins)).pack(side="left", ipadx=6)

gem_frame = ttk.Frame(mid)
gem_frame.grid(row=0, column=1, padx=20)
ttk.Label(gem_frame, text="💎 Gem Amount:", font=("Segoe UI", 10)).pack(anchor="w")
entry_gems = ttk.Entry(gem_frame, bootstyle=INFO, font=("Segoe UI", 11), width=18, justify="center")
entry_gems.pack(side="left", pady=(4, 6), padx=(0, 4))
ttk.Button(gem_frame, text="MAX", bootstyle=DANGER, command=lambda: set_max(entry_gems)).pack(side="left", ipadx=6)

ttk.Button(app, text="✨ Set Values ✨", bootstyle=(SUCCESS, OUTLINE), command=set_values).pack(pady=(10, 5), ipadx=18, ipady=4)

footer = ttk.Label(app, text="Made with love by S4IL (Packaged by VihaanVP) — feel free to contribute on our GitHub repo!↗", font=("Segoe UI", 8), foreground="#888", cursor="hand2")
footer.pack(side="bottom", pady=6)
footer.bind("<Button-1>", open_github)

app.after(500, read_current_values)
app.mainloop()