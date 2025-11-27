import time
import json
import pygetwindow as gw

from core.execute import career_lobby

# Load config
with open("config.json", "r", encoding="utf-8") as file:
  config = json.load(file)

USE_PHONE = config.get("usePhone", True)

def focus_umamusume():
  try:
    if not USE_PHONE:
      # Look for Umamusume window when not in phone mode
      windows = gw.getWindowsWithTitle("Umamusume")
      if not windows:
        print("[INFO] Umamusume window not found. Continuing without window focus.")
        return
      win = windows[0]
      print("[INFO] Found Umamusume window, focusing...")
    
      if win.isMinimized:
        win.restore()
      win.activate()
      win.maximize()
      time.sleep(0.5)
  except Exception as e:
    print(f"[INFO] Could not focus window: {e}. Continuing anyway.")

def main():
  print("Uma Auto!")
  focus_umamusume()
  
  career_lobby()

if __name__ == "__main__":
  main()
