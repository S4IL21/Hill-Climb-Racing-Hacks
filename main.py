import io
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
ICON_URL = "https://store-images.microsoft.com/image/apps.44972.9007199266379485.197540b8-dbff-480d-9e47-9e4d2941360f.a00c225f-5a41-4e33-a1e2-9d825f38c8a9"
MAX_INT_32 = 2147483647
GITHUB_URL = "https://github.com/S4IL21/Hill-Climb-Racing-Hacks"

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def parse_module_plus_offset(pm, s):
    mod_name, off_str = s.split('+', 1)
    off_str = off_str.strip().lower()
    offset = int(off_str, 16) if off_str.startswith("0x") or any(c in off_str for c in "abcdef") else int(off_str, 10)
    module = module_from_name(pm.process_handle, mod_name.strip())
    if not module:
        raise ValueError(f"Module '{mod_name}' not found.")
    return module.lpBaseOfDll + offset

def fetch_icon_image(url):
    try:
        with urllib.request.urlopen(url, timeout=8) as resp:
            data = resp.read()
        img = Image.open(io.BytesIO(data)).resize((64, 64), Image.ANTIALIAS)
        return ImageTk.PhotoImage(img)
    except Exception:
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

app = ttk.Window(title="S4IL's Hill Climb Racing Hack Menu", themename="cosmo", size=(650, 300), resizable=(False, False))
icon_image = fetch_icon_image(ICON_URL)
if icon_image: app.iconphoto(True, icon_image)

ttk.Label(app, text="S4IL's Hill Climb Racing Hack Menu", font=("Segoe UI", 12, "bold")).pack(pady=(18, 10))

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

footer = ttk.Label(app, text="Made with love by S4IL — feel free to contribute on our GitHub repo!↗", font=("Segoe UI", 8), foreground="#888", cursor="hand2")
footer.pack(side="bottom", pady=6)
footer.bind("<Button-1>", open_github)

app.after(500, read_current_values)
app.mainloop()
