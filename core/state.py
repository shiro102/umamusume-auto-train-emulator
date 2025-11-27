import re
import time

from utils.screenshot import capture_region, enhanced_screenshot
from core.ocr import extract_text, extract_number
from core.recognizer import match_template
import json
from utils.constants import get_regions_for_mode, MOOD_LIST

with open("config.json", "r", encoding="utf-8") as file:
    config = json.load(file)

USE_PHONE = config.get("usePhone", True)
SAVE_DEBUG = config.get("saveDebugImages", False)
SCENARIO = config.get("scenario", 1)

def get_config():
    return config


# Get Stat
def stat_state():
    stat_regions = {
        "spd": (310, 723, 55, 20) if not USE_PHONE else (73, 858, 65, 22),
        "sta": (405, 723, 55, 20) if not USE_PHONE else (188, 858, 60, 22),
        "pwr": (500, 723, 55, 20) if not USE_PHONE else (300, 858, 60, 22),
        "guts": (595, 723, 55, 20) if not USE_PHONE else (412, 858, 65, 22),
        "wit": (690, 723, 55, 20) if not USE_PHONE else (522, 858, 65, 22),
    }

    result = {}
    for stat, region in stat_regions.items():
        img = enhanced_screenshot(region, name=stat)
        val = extract_number(img)
        digits = "".join(filter(str.isdigit, val))
        result[stat] = int(digits) if digits.isdigit() else 0
    return result


# Check support card in each training
def check_support_card(threshold=0.8):
    SUPPORT_ICONS = {
        "spd": "assets/icons/support_card_type_spd.png",
        "sta": "assets/icons/support_card_type_sta.png",
        "pwr": "assets/icons/support_card_type_pwr.png",
        # "guts": "assets/icons/support_card_type_guts.png",
        "wit": "assets/icons/support_card_type_wit.png",
        # "friend": "assets/icons/support_card_type_friend.png",
    }

    regions = get_regions_for_mode()
    count_result = {}
    count_secondary = {}
    hasCheckedSpirit = False
    for key, icon_path in SUPPORT_ICONS.items():
        time.sleep(0.2)

        # Check spirit card for scenario 2
        if not hasCheckedSpirit and SCENARIO == 2:
            matches = match_template(
                icon_path,
                secondary_templates={
                    "spirit": "assets/icons/spirit.png",
                    "spirit-bomb": "assets/icons/spirit-bomb.png",
                },
                region=regions["SUPPORT_CARD_ICON_REGION"],
                threshold=threshold if not USE_PHONE else 0.67,
                debug=False,
                name=f"support_card_{key}",
            )
            hasCheckedSpirit = True
            count_secondary["spirit"] = len(matches.get("secondary").get("spirit"))
            count_secondary["spirit-bomb"] = len(matches.get("secondary").get("spirit-bomb"))
        else:
            matches = match_template(
                icon_path,
                region=regions["SUPPORT_CARD_ICON_REGION"],
                threshold=threshold if not USE_PHONE else 0.67,
                debug=False,
                name=f"support_card_{key}",
            )

        count_result[key] = len(matches.get("primary"))


    return count_result, count_secondary


# Get failure chance (idk how to get energy value)
def check_failure(name=None):
    regions = get_regions_for_mode()
    failure = enhanced_screenshot(regions["FAILURE_REGION"], name=f"failure_{name}")
    failure_text = extract_text(failure).lower()

    if not failure_text.startswith("failure"):
        return -1

    # SAFE CHECK
    # 1. If there is a %, extract the number before the %
    match_percent = re.search(r"failure\s+(\d{1,3})%", failure_text)
    if match_percent:
        return int(match_percent.group(1))

    # 2. If there is no %, but there is a 9, extract digits before the 9
    match_number = re.search(r"failure\s+(\d+)", failure_text)
    if match_number:
        digits = match_number.group(1)
        idx = digits.find("9")
        if idx > 0:
            num = digits[:idx]
            return int(num) if num.isdigit() else -1
        elif digits.isdigit():
            return int(digits)  # fallback

    return -1


# Check mood
def check_mood():
    regions = get_regions_for_mode()
    mood = capture_region(regions["MOOD_REGION"], name="mood")
    mood_text = extract_text(mood).upper()

    for known_mood in MOOD_LIST:
        if known_mood in mood_text:
            return known_mood

    print(f"[WARNING] Mood not recognized: {mood_text}")
    return "UNKNOWN"


# Check turn
def check_turn():
    regions = get_regions_for_mode()
    turn = enhanced_screenshot(regions["TURN_REGION"], name="turn")
    turn_text = extract_text(turn)

    if "Race Day" in turn_text:
        return "Race Day"

    if "GOAL" in turn_text:
        return "Goal"

    # sometimes easyocr misreads characters instead of numbers
    cleaned_text = (
        turn_text.replace("T", "1")
        .replace("I", "1")
        .replace("O", "0")
        .replace("S", "5")
    )

    digits_only = re.sub(r"[^\d]", "", cleaned_text)

    if digits_only:
        return int(digits_only)

    return -1


# Check year
def check_current_year():
    regions = get_regions_for_mode()
    year = enhanced_screenshot(regions["YEAR_REGION"], name="year")
    text = extract_text(year)
    return text


# Check criteria
def check_criteria():
    regions = get_regions_for_mode()
    img = enhanced_screenshot(regions["CRITERIA_REGION"], name="criteria")
    text = extract_text(img)
    return text


# Check event name
def check_event_name():
    regions = get_regions_for_mode()
    img = enhanced_screenshot(regions["EVENT_NAME_REGION"], name="event_name")
    text = extract_text(img)
    return text


# Check skill points
def check_skill_points():
    regions = get_regions_for_mode()
    img = enhanced_screenshot(regions["SKILL_PTS_REGION"], name="skill_points")
    number = extract_number(img)
    digits = "".join(filter(str.isdigit, number))
    return int(digits) if digits.isdigit() else 0


# Check skill points and handle cap
def check_skill_points_cap():
    from pymsgbox import confirm

    # Use cached config from execute.py
    from core.execute import get_config

    config = get_config()

    skill_point_cap = config.get("skill_point_cap", 100)
    current_skill_points = check_skill_points()

    print(
        f"[INFO] Current skill points: {current_skill_points}, Cap: {skill_point_cap}"
    )

    if current_skill_points > skill_point_cap:
        print(
            f"[WARNING] Skill points ({current_skill_points}) exceed cap ({skill_point_cap})"
        )

        # Show confirmation dialog
        result = confirm(
            text=f"Skill points ({current_skill_points}) exceed the cap ({skill_point_cap}).\n\nYou can:\n• Use your skill points manually, then click OK\n• Click OK without spending (automation continues)\n\nNote: This check only happens on race days.",
            title="Skill Points Cap Reached",
            buttons=["OK"],
        )

        print(
            "[INFO] Automation continuing (player may or may not have spent skill points)"
        )
        return True

    return True
