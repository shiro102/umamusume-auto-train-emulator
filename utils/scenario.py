import pyautogui
import json

# Load config
with open("config.json", "r", encoding="utf-8") as file:
  config = json.load(file)

USE_PHONE = config.get("usePhone", True)

from utils.adb_utils import adb_click
from utils.image_recognition import locate_center_on_screen

def ura():
  race_btn = locate_center_on_screen("assets/ura/ura_race_btn.png", confidence=0.8 if not USE_PHONE else 0.7, min_search_time=0.2)
  if race_btn:
    if USE_PHONE:
      adb_click(race_btn.x, race_btn.y)
    else:
      pyautogui.click(race_btn)