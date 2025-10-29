import io
import urllib.request
import webbrowser
import traceback
from tkinter import messagebox, PhotoImage
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from pymem import Pymem
from pymem.process import module_from_name
from PIL import Image, ImageTk

# ------------------ CONFIG ------------------
PROCESS_NAME = "HillClimbRacing.exe"
ADDR_COINS = "HillClimbRacing.exe+28CAD4"
ADDR_GEMS  = "HillClimbRacing.exe+28CAEC"
ICON_URL = "https://store-images.microsoft.com/image/apps.44972.9007199266379485.197540b8-dbff-480d-9e47-9e4d2941360f.a00c225f-5a41-4e33-a1e2-9d825f38c8a9"
MAX_INT_32 = 2147483647
GITHUB_URL = "https://github.com/S4IL21/Hill-Climb-Racing-Hacks"
# --------------------------------------------

def parse_module_plus_offset(pm, s):
    mod_name, off_str = s.split('+', 1)
    off_str = off_str.strip().lower()
    if off_str.startswith("0x") or any(c in off_str for c in "abcdef"):
        offset = int(off_str, 16)
    else:
        offset = int(off_str, 10)
    module = module_from_name(pm.process_handle, mod_name.strip())
    if not module:
        raise ValueError(f"Module '{mod_name}' not found.")
    return module.lpBaseOfDll + offset

def fetch_icon_image(url):
    try:
        with urllib.request.urlopen(url, timeout=8) as resp:
            data = resp.read()
        img = Image.open(io.BytesIO(data))
        img = img.resize((64, 64), Image.ANTIALIAS)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None

def attach():
    pm = Pymem(PROCESS_NAME)
    coin_addr = parse_module_plus_offset(pm, ADDR_COINS)
    gem_addr = parse_module_plus_offset(pm, ADDR_GEMS)
    return pm, coin_addr, gem_addr

def read_current_values():
    try:
        pm, coin_addr, gem_addr = attach()
        coins = pm.read_int(coin_addr)
        gems = pm.read_int(gem_addr)
        pm.close_process()
        entry_coins.delete(0, "end")
        entry_coins.insert(0, str(coins))
        entry_gems.delete(0, "end")
        entry_gems.insert(0, str(gems))
    except Exception as e:
        messagebox.showwarning("Read failed", f"⚠️ Could not read values:\n{e}")

def set_values():
    try:
        coin_text = entry_coins.get().strip()
        gem_text = entry_gems.get().strip()
        try:
            coins_val = int(coin_text, 0)
            gems_val = int(gem_text, 0)
        except ValueError:
            messagebox.showerror("Input error", "Values must be integers.")
            return

        pm, coin_addr, gem_addr = attach()
        pm.write_int(coin_addr, coins_val)
        pm.write_int(gem_addr, gems_val)

        read_coins = pm.read_int(coin_addr)
        read_gems = pm.read_int(gem_addr)
        pm.close_process()

        entry_coins.delete(0, "end")
        entry_coins.insert(0, str(read_coins))
        entry_gems.delete(0, "end")
        entry_gems.insert(0, str(read_gems))

        messagebox.showinfo("Success", f"✅ Updated!\nCoins: {read_coins}\nGems: {read_gems}")
    except Exception as e:
        tb = traceback.format_exc()
        messagebox.showerror("Error", f"❌ Could not set values:\n{e}\n\n{tb}")

def set_max(entry_widget):
    entry_widget.delete(0, "end")
    entry_widget.insert(0, str(MAX_INT_32))

def open_github(event=None):
    webbrowser.open_new(GITHUB_URL)

# ------------------ UI ------------------
app = ttk.Window(
    title="S4IL's Hill Climb Racing Hack Menu",
    themename="cosmo",
    size=(650, 300),
    resizable=(False, False)
)

# Set icon
icon_image = fetch_icon_image(ICON_URL)
if icon_image:
    app.iconphoto(True, icon_image)

# Title label
ttk.Label(
    app,
    text="S4IL's Hill Climb Racing Hack Menu",
    font=("Segoe UI", 12, "bold")
).pack(pady=(18, 10))

# Coin + Gem input frame
mid = ttk.Frame(app)
mid.pack(pady=10)

# --- Coins ---
coin_frame = ttk.Frame(mid)
coin_frame.grid(row=0, column=0, padx=20)
ttk.Label(coin_frame, text="💰 Coin Amount:", font=("Segoe UI", 10)).pack(anchor="w")
entry_coins = ttk.Entry(coin_frame, bootstyle=INFO, font=("Segoe UI", 11), width=18, justify="center")
entry_coins.pack(side="left", pady=(4, 6), padx=(0, 4))
ttk.Button(coin_frame, text="MAX", bootstyle=DANGER, command=lambda: set_max(entry_coins)).pack(side="left", ipadx=6)

# --- Gems ---
gem_frame = ttk.Frame(mid)
gem_frame.grid(row=0, column=1, padx=20)
ttk.Label(gem_frame, text="💎 Gem Amount:", font=("Segoe UI", 10)).pack(anchor="w")
entry_gems = ttk.Entry(gem_frame, bootstyle=INFO, font=("Segoe UI", 11), width=18, justify="center")
entry_gems.pack(side="left", pady=(4, 6), padx=(0, 4))
ttk.Button(gem_frame, text="MAX", bootstyle=DANGER, command=lambda: set_max(entry_gems)).pack(side="left", ipadx=6)

# Set button
ttk.Button(
    app,
    text="✨ Set Values ✨",
    bootstyle=(SUCCESS, OUTLINE),
    command=set_values
).pack(pady=(10, 5), ipadx=18, ipady=4)

# Footer
footer = ttk.Label(
    app, 
    text="Made with love by S4IL — feel free to contribute on our GitHub repo!↗", 
    font=("Segoe UI", 8), 
    foreground="#888", 
    cursor="hand2"
)
footer.pack(side="bottom", pady=6)
footer.bind("<Button-1>", open_github)

# Populate current values on start
app.after(500, read_current_values)

app.mainloop()
