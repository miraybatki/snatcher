import pyautogui
from pynput import mouse
from threading import Thread, Timer          # ← ➊ Timer eklendi
from tkinter import Tk, Button
import os

# ----------  ALAN BOYUTU ve KONUMU  ----------
AREA_W, AREA_H = 1250, 810
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
AREA_X = (SCREEN_WIDTH - AREA_W) // 2
AREA_Y = 80

REGION_LEFT  = (AREA_X, AREA_Y, AREA_W // 2, AREA_H)
REGION_RIGHT = (AREA_X + AREA_W // 2, AREA_Y, AREA_W // 2, AREA_H)
# ----------------------------------------------

SAVE_DIR = "pages"
os.makedirs(SAVE_DIR, exist_ok=True)
listener = None
DELAY = 0.75                                  # ← ➋ Gecikme (sn)

def next_number():
    nums = [int(f.split(".")[0]) for f in os.listdir(SAVE_DIR)
            if f.endswith(".jpg") and f.split(".")[0].isdigit()]
    return max(nums) + 1 if nums else 1

def save_jpg(img, num):
    path = os.path.join(SAVE_DIR, f"{num}.jpg")
    img.convert("RGB").save(path, "JPEG")
    print(f"[✓] {path}")

def capture_both():
    n = next_number()
    save_jpg(pyautogui.screenshot(region=REGION_LEFT),  n)
    save_jpg(pyautogui.screenshot(region=REGION_RIGHT), n + 1)

def on_click(x, y, button, pressed):
    if pressed:
        Timer(DELAY, capture_both).start()     # 0.75 s sonra çalış

def start_listener():
    global listener
    if listener is None or not listener.running:
        listener = mouse.Listener(on_click=on_click)
        listener.start()
        print("🎬 Dinleme başladı")

def stop_listener():
    global listener
    if listener:
        listener.stop()
        listener = None
        print("🛑 Dinleme durdu")

# ----------  GUI  ----------
root = Tk()
root.title("Ortalanmış 2'li Screenshot")
root.geometry("300x100")

Button(root, text="Başlat", command=lambda: Thread(target=start_listener).start(),
       bg="green", fg="white", width=15).pack(pady=10)
Button(root, text="Durdur", command=stop_listener,
       bg="red", fg="white", width=15).pack()

root.mainloop()
