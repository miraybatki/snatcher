import os
import random
from threading import Thread, Timer
from tkinter import Tk, Button

import pyautogui
from PIL import Image  # Pillow
from pynput import mouse

"""
snatcher – auto‑click edition (random delay, no duplicate SS)
------------------------------------------------------------
• Waits **1.75 s** after each click (human *or* simulated), then grabs a
  centred 1050 × 1360 screenshot and stores it as `pages/0001.jpg`, …
• Auto‑click loop now fires every **random 2.5 – 3.0 s** and *does not*
  call `capture_single()` directly. The listener triggered by that
  simulated click handles the screenshot, preventing duplicate images.
• Start → first click sets anchor → loop begins. Stop cancels everything.
• Create PDF stitches current JPGs into `books/bookN.pdf`.
"""

# ------------ AREA DEFINITION ------------
AREA_W, AREA_H = 1050, 1360
SCREEN_W, SCREEN_H = pyautogui.size()
AREA_X = (SCREEN_W - AREA_W) // 2
AREA_Y = 93
REGION = (AREA_X, AREA_Y, AREA_W, AREA_H)

SAVE_DIR = "pages"
BOOK_DIR = "books"
os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(BOOK_DIR, exist_ok=True)

# ---- settings ----
DELAY_SCREENSHOT = 1.75      # wait before taking SS after a click
CLICK_MIN, CLICK_MAX = 2.5, 3.0  # random interval range (seconds)

# ---- globals ----
listener = None
anchor_pos = None
auto_click_active = False

# ---------- helpers ----------

def next_number(folder: str) -> int:
    nums = [int(f.split(".")[0]) for f in os.listdir(folder)
            if f.lower().endswith(".jpg") and f.split(".")[0].isdigit()]
    return max(nums) + 1 if nums else 1


def save_jpg(img: Image.Image, num: int):
    path = os.path.join(SAVE_DIR, f"{num:04d}.jpg")
    img.convert("RGB").save(path, "JPEG", quality=90)
    print(f"[✓] {path}")

# ---------- capture ----------

def capture_single():
    num = next_number(SAVE_DIR)
    img = pyautogui.screenshot(region=REGION)
    save_jpg(img, num)

# ---------- auto‑click logic ----------

def auto_click_loop():
    global auto_click_active
    if not auto_click_active or anchor_pos is None:
        return  # cancelled

    x, y = anchor_pos
    pyautogui.click(x, y)                # generates an OS‑level click
    # listener will handle the screenshot with its own delay

    next_delay = random.uniform(CLICK_MIN, CLICK_MAX)
    Timer(next_delay, auto_click_loop).start()

# ---------- mouse listener ----------

def on_click(x, y, button, pressed):
    global anchor_pos, auto_click_active
    if pressed:
        Timer(DELAY_SCREENSHOT, capture_single).start()
        if anchor_pos is None:           # first tangible click sets anchor
            anchor_pos = (x, y)
            auto_click_active = True
            Timer(random.uniform(CLICK_MIN, CLICK_MAX), auto_click_loop).start()
            print(f"🔂 Auto‑clicking every {CLICK_MIN}–{CLICK_MAX}s at {anchor_pos}")

# ---------- listener controls ----------

def start_listener():
    global listener, anchor_pos, auto_click_active
    anchor_pos = None
    auto_click_active = False
    if listener is None or not listener.running:
        listener = mouse.Listener(on_click=on_click)
        listener.start()
        print("🎬 Listener started – click to set anchor")


def stop_listener():
    global listener, auto_click_active
    auto_click_active = False
    if listener is not None:
        listener.stop()
        listener = None
        print("🛑 Listener & auto‑click stopped")

# ---------- PDF builder ----------

def build_pdf():
    imgs = sorted([
        os.path.join(SAVE_DIR, f) for f in os.listdir(SAVE_DIR)
        if f.lower().endswith(".jpg") and f.split(".")[0].isdigit()
    ], key=lambda p: int(os.path.splitext(os.path.basename(p))[0]))
    if not imgs:
        print("[!] No pages to convert")
        return

    pages = [Image.open(img).convert("RGB") for img in imgs]
    existing = [f for f in os.listdir(BOOK_DIR) if f.startswith("book") and f.endswith(".pdf")]
    nums = [int(f[4:-4]) for f in existing if f[4:-4].isdigit()]
    next_num = max(nums) + 1 if nums else 1
    pdf_path = os.path.join(BOOK_DIR, f"book{next_num}.pdf")
    pages[0].save(pdf_path, save_all=True, append_images=pages[1:])
    print(f"[✓] PDF saved -> {pdf_path}")

# ---------- GUI ----------
root = Tk()
root.title("snatcher – random auto‑click")
root.geometry("330x150")

Button(root, text="Start",  command=lambda: Thread(target=start_listener).start(),
       bg="#28a745", fg="white", width=18).pack(pady=5)
Button(root, text="Stop",   command=stop_listener,
       bg="#d73a49", fg="white", width=18).pack(pady=5)
Button(root, text="Create PDF", command=build_pdf,
       bg="#0366d6", fg="white", width=18).pack(pady=5)

root.mainloop()
