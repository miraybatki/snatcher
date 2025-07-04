import os
import random
from threading import Thread, Timer
from tkinter import Tk, Button

import pyautogui
from PIL import Image  # Pillow
from pynput import mouse

"""
snatcher – auto‑click edition (random delay + split region)
------------------------------------------------------------
• Takes a screenshot from a centred 1586×1016 region, splits it into
  two halves (left and right pages), and saves as 0001.jpg, 0002.jpg …
• Auto-clicks at random intervals (4.5–5.0 s), waits 4 s, then saves.
• Anchor point set on first click. Stop halts all activity.
• PDF combines all pages from `pages/` into `books/bookN.pdf`
"""

# ------------ AREA DEFINITION ------------
AREA_W, AREA_H = 1586, 1016
SCREEN_W, SCREEN_H = pyautogui.size()
AREA_X = (SCREEN_W - AREA_W) // 2
AREA_Y = 34
REGION = (AREA_X, AREA_Y, AREA_W, AREA_H)

SAVE_DIR = "pages"
BOOK_DIR = "books"
os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(BOOK_DIR, exist_ok=True)

# ---- settings ----
DELAY_SCREENSHOT = 4.0
CLICK_MIN, CLICK_MAX = 4.5, 5.0

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

def capture_split():
    num = next_number(SAVE_DIR)
    full_img = pyautogui.screenshot(region=REGION).convert("RGB")
    left_box = (0, 0, AREA_W // 2, AREA_H)
    right_box = (AREA_W // 2, 0, AREA_W, AREA_H)
    left_img = full_img.crop(left_box)
    right_img = full_img.crop(right_box)
    save_jpg(left_img, num)
    save_jpg(right_img, num + 1)

# ---------- auto-click logic ----------

def auto_click_loop():
    global auto_click_active
    if not auto_click_active or anchor_pos is None:
        return
    x, y = anchor_pos
    pyautogui.click(x, y)
    Timer(random.uniform(CLICK_MIN, CLICK_MAX), auto_click_loop).start()

# ---------- mouse listener ----------

def on_click(x, y, button, pressed):
    global anchor_pos, auto_click_active
    if pressed:
        Timer(DELAY_SCREENSHOT, capture_split).start()
        if anchor_pos is None:
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
root.title("snatcher – split screenshot")
root.geometry("330x150")

Button(root, text="Start",  command=lambda: Thread(target=start_listener).start(),
       bg="#28a745", fg="white", width=18).pack(pady=5)
Button(root, text="Stop",   command=stop_listener,
       bg="#d73a49", fg="white", width=18).pack(pady=5)
Button(root, text="Create PDF", command=build_pdf,
       bg="#0366d6", fg="white", width=18).pack(pady=5)

root.mainloop()
