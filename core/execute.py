import os
import time
import json
from datetime import datetime

import pyautogui
import cv2
import numpy as np

from core.state import (
    check_support_card,
    check_failure,
    check_turn,
    check_mood,
    check_current_year,
    check_criteria,
    check_event_name,
    check_skill_points_cap,
)
from core.logic import (
    do_something,
    do_something_fallback,
    check_training_unsafe,
    MAX_FAILURE,
)
from core.recognizer import is_infirmary_active, match_template
from utils.constants import MOOD_LIST
from utils.adb_utils import (
    adb_click,
    adb_move_to,
    adb_mouse_down,
    adb_mouse_up,
    adb_scroll,
    auto_connect_mumu,
    check_mumu_resolution,
    get_adb_controller,
)
from utils.image_recognition import locate_center_on_screen, locate_on_screen
from utils.scenario import ura

pyautogui.useImageNotFoundException(False)


def is_racing_available(year):
    """Check if racing is available based on the current year/month"""
    year_parts = year.split(" ")
    # No races in July and August (summer break)
    if len(year_parts) > 3 and year_parts[3] in ["Jul", "Aug"]:
        return False
    return True


# Load config once at startup
with open("config.json", "r", encoding="utf-8") as file:
    config = json.load(file)

with open("events.json", "r", encoding="utf-8") as file:
    predefined_events = json.load(file)

MINIMUM_MOOD = config["minimum_mood"]
PRIORITIZE_G1_RACE = config["prioritize_g1_race"]
USE_PHONE = config.get("usePhone", False)
NEW_YEAR_EVENT_DONE = False
FIRST_TURN_DONE = False


training_types = {
    "spd": (
        "assets/icons/train_spd.png"
        if not USE_PHONE
        else "assets/icons/train_spd_phone.png"
    ),
    "sta": (
        "assets/icons/train_sta.png"
        if not USE_PHONE
        else "assets/icons/train_sta_phone.png"
    ),
    "pwr": (
        "assets/icons/train_pwr.png"
        if not USE_PHONE
        else "assets/icons/train_pwr_phone.png"
    ),
    "guts": (
        "assets/icons/train_guts.png"
        if not USE_PHONE
        else "assets/icons/train_guts_phone.png"
    ),
    "wit": (
        "assets/icons/train_wit.png"
        if not USE_PHONE
        else "assets/icons/train_wit_phone.png"
    ),
}


def get_config():
    return config


def click(img, confidence=0.8, minSearch=2, click=1, text=""):
    btn = locate_center_on_screen(img, confidence=confidence, min_search_time=minSearch)
    if btn:
        if text:
            print(text)

        # Check if usePhone is enabled in config
        if USE_PHONE:
            # Use ADB for phone emulation
            # Auto-detect Mumu if not already connected
            if not get_adb_controller().is_connected():
                print("[INFO] Auto-detecting Mumu instance...")
                auto_connect_mumu()

                # Check resolution for phone mode
                print("[INFO] Checking Mumu resolution...")
                if not check_mumu_resolution(720, 1280):
                    print(
                        "[WARNING] Mumu resolution is not 720x1280. This may cause issues."
                    )
                    print(
                        "[INFO] Please set Mumu resolution to 720x1280 for optimal performance."
                    )

            for i in range(click):
                adb_move_to(btn.x, btn.y, duration=0.175)
                adb_click(btn.x, btn.y)
                if i < click - 1:  # Add interval between multiple clicks
                    time.sleep(0.1)
        else:
            # Use regular pyautogui
            pyautogui.moveTo(btn, duration=0.175)
            pyautogui.click(clicks=click)

        return True

    return False


def click_event_choice(choice_number, minSearch=0.2, confidence=0.8):
    """Special function for clicking event choices with higher confidence to avoid confusion"""
    img_path = f"assets/icons/event_choice_1.png"
    # Use higher confidence for event choices to avoid confusion between similar images
    btn = locate_center_on_screen(
        img_path, confidence=confidence, min_search_time=minSearch
    )
    if btn:
        print(
            f"[INFO] Event choice 1 found: {btn}, selecting option choice {choice_number} below it"
        )

        if choice_number != 1:
            adjusted_btn = (btn.x, btn.y + (choice_number - 1) * 115)
            target_x, target_y = adjusted_btn
        else:
            target_x, target_y = btn.x, btn.y

        # Check if usePhone is enabled in config
        if USE_PHONE:
            # Use ADB for phone emulation
            adb_move_to(target_x, target_y, duration=0.175)
            adb_click(target_x, target_y)
        else:
            # Use regular pyautogui
            pyautogui.moveTo(target_x, target_y, duration=0.175)
            pyautogui.click()

        return True
    return False


def go_to_training():
    return click(
        "assets/buttons/training_btn.png", confidence=0.8 if not USE_PHONE else 0.7
    )


def click_guts_button():
    """Dedicated function to click the guts training button with fallback templates"""
    btn = locate_center_on_screen(
        training_types["guts"], confidence=0.8 if not USE_PHONE else 0.65
    )

    # Try alternative templates if not found
    if not btn:
        alt_2 = training_types["guts"].replace(".png", "_2.png")
        alt_3 = training_types["guts"].replace(".png", "_3.png")
        btn = locate_center_on_screen(
            alt_2, confidence=0.8 if not USE_PHONE else 0.65
        ) or locate_center_on_screen(alt_3, confidence=0.8 if not USE_PHONE else 0.65)

    if btn:
        if USE_PHONE:
            adb_move_to(btn.x, btn.y, duration=0.175)
            time.sleep(0.2)
        else:
            pyautogui.moveTo(btn, duration=0.175)
            time.sleep(0.2)
        return True
    else:
        print("[INFO] Guts training icon not found; continuing without pre-move.")
        return False


def check_training():
    results = {}
    last_mouse_pos = None

    ### move to guts training first
    click_guts_button()

    for key, icon_path in training_types.items():
        pos = locate_center_on_screen(
            icon_path, confidence=0.8 if not USE_PHONE else 0.65
        )

        # Check for second icon option if first one is not found
        if not pos:
            pos = locate_center_on_screen(
                icon_path.replace(".png", "_2.png"),
                confidence=0.8 if not USE_PHONE else 0.65,
            )

        # Check for third icon option if second one is not found
        if not pos:
            pos = locate_center_on_screen(
                icon_path.replace(".png", "_3.png"),
                confidence=0.8 if not USE_PHONE else 0.65,
            )

        if pos:
            if USE_PHONE:
                adb_mouse_down(pos.x, pos.y)
                last_mouse_pos = (pos.x, pos.y)
            else:
                pyautogui.moveTo(pos, duration=0.1)
                pyautogui.mouseDown()

            support_counts = check_support_card()
            total_support = sum(support_counts.values())
            failure_chance = check_failure()
            results[key] = {
                "support": support_counts,
                "total_support": total_support,
                "failure": failure_chance,
            }
            print(f"[{key.upper()}] → {support_counts}, Fail: {failure_chance}%")
            time.sleep(0.1)

    if USE_PHONE:
        # For ADB, release the mouse at the last position where it was pressed
        if last_mouse_pos:
            adb_mouse_up(last_mouse_pos[0], last_mouse_pos[1])
        else:
            # Fallback to center if no position was recorded
            adb_mouse_up(360, 640)  # Center of 720x1280 screen
    else:
        pyautogui.mouseUp()

    click(img="assets/buttons/back_btn.png")
    return results


def do_train(train):
    if USE_PHONE:
        train_btn = locate_center_on_screen(
            f"assets/icons/train_{train}_phone.png", confidence=0.7
        )

        if not train_btn:
            train_btn = locate_center_on_screen(
                f"assets/icons/train_{train}_phone_2.png", confidence=0.7
            )
    else:
        train_btn = locate_center_on_screen(
            f"assets/icons/train_{train}.png", confidence=0.8
        )

    print(f"[INFO] Training button found: {train_btn}")
    if train_btn:
        if USE_PHONE:
            print(f"[INFO] Moving to {train} found at {train_btn}")
            adb_move_to(train_btn.x, train_btn.y, duration=0.15)
            adb_click(train_btn.x, train_btn.y)
            time.sleep(0.1)
            adb_click(train_btn.x, train_btn.y)
        else:
            pyautogui.moveTo(train_btn, duration=0.15)
            pyautogui.tripleClick(train_btn, interval=0.1, duration=0.2)


def do_rest():
    rest_btn = locate_center_on_screen("assets/buttons/rest_btn.png", confidence=0.8)
    rest_summber_btn = locate_center_on_screen(
        "assets/buttons/rest_summer_btn.png", confidence=0.6
    )

    if rest_btn:
        if USE_PHONE:
            adb_move_to(rest_btn.x, rest_btn.y, duration=0.15)
            adb_click(rest_btn.x, rest_btn.y)
        else:
            pyautogui.moveTo(rest_btn, duration=0.15)
            pyautogui.click(rest_btn)
    elif rest_summber_btn:
        if USE_PHONE:
            adb_move_to(rest_summber_btn.x, rest_summber_btn.y, duration=0.15)
            adb_click(rest_summber_btn.x, rest_summber_btn.y)
        else:
            pyautogui.moveTo(rest_summber_btn, duration=0.15)
            pyautogui.click(rest_summber_btn)


def do_recreation():
    recreation_btn = locate_center_on_screen(
        "assets/buttons/recreation_btn.png", confidence=0.8 if not USE_PHONE else 0.7
    )
    recreation_summer_btn = locate_center_on_screen(
        "assets/buttons/rest_summer_btn.png", confidence=0.8 if not USE_PHONE else 0.7
    )

    if recreation_btn:
        if USE_PHONE:
            adb_move_to(recreation_btn.x, recreation_btn.y, duration=0.15)
            adb_click(recreation_btn.x, recreation_btn.y)
        else:
            pyautogui.moveTo(recreation_btn, duration=0.15)
            pyautogui.click(recreation_btn)
    elif recreation_summer_btn:
        if USE_PHONE:
            adb_move_to(recreation_summer_btn.x, recreation_summer_btn.y, duration=0.15)
            adb_click(recreation_summer_btn.x, recreation_summer_btn.y)
        else:
            pyautogui.moveTo(recreation_summer_btn, duration=0.15)
            pyautogui.click(recreation_summer_btn)


def do_race(prioritize_g1=False):
    click(
        img="assets/buttons/races_btn.png",
        minSearch=10,
        confidence=0.8 if not USE_PHONE else 0.7,
    )
    click(
        img="assets/buttons/ok_btn.png",
        minSearch=0.7,
        confidence=0.8 if not USE_PHONE else 0.7,
    )

    found = race_select(prioritize_g1=prioritize_g1)
    if not found:
        print("[INFO] No race found.")
        return False

    race_prep()
    time.sleep(1)
    after_race()
    return True


def race_day():
    # Check skill points cap before race day (if enabled)
    # Use cached config
    config = get_config()
    enable_skill_check = config.get("enable_skill_point_check", True)

    if enable_skill_check:
        print("[INFO] Race Day - Checking skill points cap...")
        check_skill_points_cap()

    click(
        img="assets/buttons/race_day_btn.png",
        minSearch=10,
        confidence=0.8 if not USE_PHONE else 0.65,
    )

    click(img="assets/buttons/ok_btn.png", minSearch=0.7)
    time.sleep(0.5)

    for i in range(2):
        click(img="assets/buttons/race_btn.png", minSearch=2)
        time.sleep(0.5)

    race_prep()
    time.sleep(1)
    after_race()


def save_debug_region_image(
    screenshot, region, template_path, match_result, debug_dir="debug_images"
):
    """Save debug images with region information for manual verification"""
    try:
        if not os.path.exists(debug_dir):
            os.makedirs(debug_dir)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Extract region from screenshot
        x, y, w, h = region
        region_screenshot = screenshot[y : y + h, x : x + w]

        # Save the region screenshot
        region_path = os.path.join(debug_dir, f"debug_region_{timestamp}.png")
        cv2.imwrite(region_path, region_screenshot)

        # Save the template
        template = cv2.imread(template_path, cv2.IMREAD_COLOR)
        if template is not None:
            template_path_debug = os.path.join(
                debug_dir, f"debug_template_{timestamp}.png"
            )
            cv2.imwrite(template_path_debug, template)

        # Save full screenshot with region highlighted
        full_screenshot = screenshot.copy()
        cv2.rectangle(full_screenshot, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(
            full_screenshot,
            f"Region: {region}",
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
        )

        full_path = os.path.join(debug_dir, f"debug_full_screenshot_{timestamp}.png")
        cv2.imwrite(full_path, full_screenshot)

        # Save match result info
        result_info = f"Match found: {match_result is not None}"
        if match_result:
            result_info += f" at ({match_result.x}, {match_result.y})"

        info_path = os.path.join(debug_dir, f"debug_info_{timestamp}.txt")
        with open(info_path, "w") as f:
            f.write(f"Template: {template_path}\n")
            f.write(f"Region: {region}\n")
            f.write(f"Result: {result_info}\n")
            f.write(f"Timestamp: {timestamp}\n")

        print(
            f"[DEBUG] Saved debug images: {region_path}, {template_path_debug}, {full_path}, {info_path}"
        )
        print(f"[DEBUG] {result_info}")

    except Exception as e:
        print(f"[DEBUG] Failed to save debug images: {e}")


def get_screenshot_for_debug():
    """Get screenshot for debugging purposes"""
    try:
        if USE_PHONE:
            from utils.adb_utils import get_adb_controller

            controller = get_adb_controller()
            if controller and controller.is_connected():
                screenshot = controller.take_screenshot()
                if screenshot is not None:
                    return cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
        else:
            # For desktop, we'll need to take a screenshot
            screenshot = pyautogui.screenshot()
            return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    except Exception as e:
        print(f"[DEBUG] Failed to get screenshot: {e}")
        return None


def race_select(prioritize_g1=False):

    time.sleep(0.2)

    if prioritize_g1:
        print("[INFO] Looking for G1 race.")
        for i in range(2):
            race_card = match_template("assets/ui/g1_race.png", threshold=0.85)
            print(f"[INFO] Race card found: {race_card}")
            if race_card:
                for x, y, w, h in race_card:
                    region = (x, y, 310, 90) if not USE_PHONE else (x, y, 370, 100)

                    # Debug: Save screenshot before detection
                    # debug_screenshot = get_screenshot_for_debug()

                    match_aptitude = locate_center_on_screen(
                        "assets/ui/match_track.png",
                        confidence=0.7,
                        min_search_time=0.7,
                        region=region,
                    )

                    # Debug: Save images with region information
                    # if debug_screenshot is not None:
                    #   save_debug_region_image(debug_screenshot, region, "assets/ui/match_track.png", match_aptitude)

                    if match_aptitude:
                        print("[INFO] G1 race found.")
                        if USE_PHONE:
                            adb_move_to(
                                match_aptitude.x, match_aptitude.y, duration=0.2
                            )
                            adb_click(match_aptitude.x, match_aptitude.y)
                        else:
                            pyautogui.moveTo(match_aptitude, duration=0.2)
                            pyautogui.click()
                        for i in range(2):
                            race_btn = locate_center_on_screen(
                                "assets/buttons/race_btn.png",
                                confidence=0.8,
                                min_search_time=2,
                            )
                            if race_btn:
                                if USE_PHONE:
                                    adb_move_to(race_btn.x, race_btn.y, duration=0.2)
                                    adb_click(race_btn.x, race_btn.y)
                                else:
                                    pyautogui.moveTo(race_btn, duration=0.2)
                                    pyautogui.click(race_btn)
                                time.sleep(0.5)
                        return True

            for i in range(4):
                if USE_PHONE:
                    adb_scroll(150, 360, 800)
                else:
                    pyautogui.scroll(-300)

        return False
    else:
        print("[INFO] Looking for race.")
        for i in range(4):
            # Debug: Save screenshot before detection (for non-G1 races)
            # debug_screenshot = get_screenshot_for_debug()

            match_aptitude = locate_center_on_screen(
                "assets/ui/match_track.png", confidence=0.8, min_search_time=0.7
            )

            # Debug: Save images without region (full screen search)
            # if debug_screenshot is not None:
            #   # Create a mock region for full screen (0, 0, width, height)
            #   height, width = debug_screenshot.shape[:2]
            #   full_region = (0, 0, width, height)
            #   save_debug_region_image(debug_screenshot, full_region, "assets/ui/match_track.png", match_aptitude)

            if match_aptitude:
                print("[INFO] Race found.")
                if USE_PHONE:
                    adb_move_to(match_aptitude.x, match_aptitude.y, duration=0.2)
                    adb_click(match_aptitude.x, match_aptitude.y)
                else:
                    pyautogui.moveTo(match_aptitude, duration=0.2)
                    pyautogui.click(match_aptitude)

                for i in range(2):
                    race_btn = locate_center_on_screen(
                        "assets/buttons/race_btn.png", confidence=0.8, min_search_time=2
                    )
                    if race_btn:
                        if USE_PHONE:
                            adb_move_to(race_btn.x, race_btn.y, duration=0.2)
                            adb_click(race_btn.x, race_btn.y)
                        else:
                            pyautogui.moveTo(race_btn, duration=0.2)
                            pyautogui.click(race_btn)
                        time.sleep(0.5)
                return True

            for i in range(4):
                if USE_PHONE:
                    adb_scroll(150, 360, 800)
                else:
                    pyautogui.scroll(-300)

        return False


def race_prep():
    time.sleep(3.5)
    print(f"[INFO] Finding view results button at time: {time.time()}")
    view_result_btn = locate_center_on_screen(
        "assets/buttons/view_results.png",
        confidence=0.8 if not USE_PHONE else 0.6,
        min_search_time=12,
    )
    print(f"[INFO] View result button found at time: {time.time()}")

    if view_result_btn:
        if USE_PHONE:
            adb_click(view_result_btn.x, view_result_btn.y)
        else:
            pyautogui.click(view_result_btn)

        time.sleep(1.5)

        for i in range(2):
            if USE_PHONE:
                # For ADB, we'll do 3 separate clicks instead of tripleClick
                for j in range(3):
                    adb_click(360, 640)  # Click center of screen
                    time.sleep(0.1)
            else:
                pyautogui.tripleClick(interval=0.3)
            time.sleep(1.5)


def after_race():
    print(f"[INFO] Finding after race first next button at time: {time.time()}")
    click(img="assets/buttons/next_btn.png", minSearch=2)
    print(f"[INFO] Finding after race first next button at time: {time.time()}")
    time.sleep(2)  # Raise a bit
    # pyautogui.click()
    print(f"[INFO] Finding after race second next button at time: {time.time()}")
    click(img="assets/buttons/next2_btn.png", minSearch=3)
    print(f"[INFO] Finding after race second next button at time: {time.time()}")


def career_lobby():
    global FIRST_TURN_DONE
    global NEW_YEAR_EVENT_DONE

    # Program start
    while True:

        year = check_current_year()
        event_name = check_event_name()

        print(f"[INFO] Event Name: {event_name}")

        ## First check, event
        if (
            year == "Classic Year Early Jan" and not NEW_YEAR_EVENT_DONE
        ):  # 2nd New Year Event for energy
            print("[ACTION] Checking for 2nd New Year Event for energy")
            if click_event_choice(2, minSearch=1, confidence=0.9):
                print("[ACTION] Clicking choice 2 for 2nd New Year Event for energy")
                NEW_YEAR_EVENT_DONE = True
                continue
            else:
                if click_event_choice(1, minSearch=0.2, confidence=0.9):
                    print(
                        "[ACTION] Cannot find 2nd New Year Event for energy, clicking choice 1"
                    )
                    NEW_YEAR_EVENT_DONE = True
                    continue
        else:
            for predefine_event_name, predefine_event_data in predefined_events.items():
                if predefine_event_data["key"].lower() in event_name.lower():
                    print(
                        f"[ACTION] {predefine_event_name} event found, clicking choice {predefine_event_data['choice']}"
                    )
                    if click_event_choice(
                        predefine_event_data["choice"], minSearch=0.1, confidence=0.9
                    ):
                        print(
                            f"[ACTION] Clicked choice {predefine_event_data['choice']}"
                        )
                        continue

            if click_event_choice(1, minSearch=0.1, confidence=0.9):
                print("[ACTION] Clicked choice 1")
                continue

            # support event belows, auto choose 1st option if not specified
            # if (
            #     "extra training" in event_name.lower()
            # ):  # Always choose rest option for extra training event (depends on the Uma), change if needed
            #     print(
            #         "[ACTION] Extra Training event found, clicking choice 2 for energy"
            #     )
            #     if click_event_choice(2, minSearch=0.1, confidence=0.9):
            #         print("[ACTION] Clicked choice 2")
            #         continue
            # elif (
            #     "lovely training weather" in event_name.lower()
            # ):  # FM event, choose 3rd for Perfect Condition
            #     print(
            #         "[ACTION] Lovely Training Weather event found, clicking choice 3 for Perfect Condition"
            #     )
            #     if click_event_choice(3, minSearch=0.1, confidence=0.9):
            #         print("[ACTION] Clicked choice 3")
            #         continue
            # elif (
            #     "preparing my special move" in event_name.lower()
            # ):  # Biko Pegasus event, choose 2nd for energy
            #     print(
            #         "[ACTION] Preparing My Special Move event found, clicking choice 2 for energy"
            #     )
            #     if click_event_choice(2, minSearch=0.1, confidence=0.9):
            #         print("[ACTION] Clicked choice 2")
            #         continue
            # elif (
            #     "solo nighttime run" in event_name.lower()
            # ):  # Manhattan Cafe event, choose 2nd for energy
            #     print(
            #         "[ACTION] Solo Nighttime Run event found, clicking choice 2 for energy"
            #     )
            #     if click_event_choice(2, minSearch=0.1, confidence=0.9):
            #         print("[ACTION] Clicked choice 2")
            #         continue
            # elif (
            #     "happenstance introduced" in event_name.lower()
            # ):  # Agnes Tachyon event, choose 2nd for wit
            #     print("[ACTION] Happenstance event found, clicking choice 2 for wit")
            #     if click_event_choice(2, minSearch=0.1, confidence=0.9):
            #         print("[ACTION] Clicked choice 2")
            #         continue
            # elif (
            #     "just an acupuncturist" in event_name.lower()
            # ):  # Just an acupuncturist event, choose 1st for energy
            #     print("[ACTION] Acupuncturist event found, clicking choice 4")
            #     if click_event_choice(4, minSearch=0.1, confidence=0.9):
            #         print("[ACTION] Clicked choice 4")

            #     time.sleep(0.5)
            #     if click_event_choice(1, minSearch=0.1, confidence=0.9):
            #         print("[ACTION] Clicked choice 1")
            #         continue
            # else:
            #     if click_event_choice(1, minSearch=0.1, confidence=0.9):
            #         print("[ACTION] Clicked choice 1")
            #         continue

        ### Second check, inspiration
        if click(
            img="assets/buttons/inspiration_btn.png",
            minSearch=0.2,
            text="[INFO] Inspiration found.",
            confidence=0.65,
        ):
            continue

        ### Third check, next button
        if click(
            img="assets/buttons/next_btn.png",
            minSearch=0.2,
            confidence=0.8 if not USE_PHONE else 0.7,
        ):
            continue

        ### Fourth check, cancel button
        if click(
            img="assets/buttons/cancel_btn.png",
            minSearch=0.2,
            confidence=0.8 if not USE_PHONE else 0.7,
        ):
            continue

        ### Check if current menu is in career lobby
        tazuna_hint = locate_center_on_screen(
            "assets/ui/tazuna_hint.png", confidence=0.8, min_search_time=0.2
        )

        if tazuna_hint is None:
            print("[INFO] Should be in career lobby.")
            continue

        time.sleep(0.5)

        ### Check if there is debuff status
        debuffed = locate_on_screen(
            "assets/buttons/infirmary_btn2.png",
            confidence=0.8 if not USE_PHONE else 0.7,
            min_search_time=1,
        )
        if debuffed:
            if is_infirmary_active(
                (debuffed.left, debuffed.top, debuffed.width, debuffed.height)
            ):
                if USE_PHONE:
                    adb_click(debuffed.x, debuffed.y)
                else:
                    pyautogui.click(debuffed)
                print("[INFO] Character has debuff, go to infirmary instead.")
                continue

        mood = check_mood()
        mood_index = MOOD_LIST.index(mood)
        minimum_mood = MOOD_LIST.index(MINIMUM_MOOD)
        criteria = check_criteria()
        turn = check_turn()

        print(
            "\n=======================================================================================\n"
        )
        print(f"Year: {year}")
        print(f"Mood: {mood}")
        print(f"Turn Left: {turn}")
        print(f"Criteria: {criteria} \n")
        
        # URA SCENARIO
        if year == "Finale Season" and turn == "Race Day":
            print("[INFO] URA Finale")
            ura()
            for i in range(2):
                if click(img="assets/buttons/race_btn.png", minSearch=2):
                    time.sleep(0.5)

            race_prep()
            time.sleep(1)
            after_race()
            continue

        # If calendar is race day, do race
        if turn == "Race Day" and year != "Finale Season":
            print("[INFO] Race Day.")
            race_day()
            continue

        # Mood check, not checking in the first turn of Pre-Debut
        if mood_index < minimum_mood and not (
            year == "Junior Year Pre-Debut" and not FIRST_TURN_DONE
        ):
            print("[INFO] Mood is low, trying recreation to increase mood")
            do_recreation()
            continue

        if not FIRST_TURN_DONE:
            FIRST_TURN_DONE = True

        # Check if goals is not met criteria AND it is not Pre-Debut AND turn is less than 10 AND Goal is already achieved (for desktop only)
        if config.get("check_goals", False) and (
            criteria.split(" ")[0] != "criteria"
            and year != "Junior Year Pre-Debut"
            and turn < 5
            and (criteria != "Goal Achieved" or "fan" in criteria.lower() or criteria != "")
        ):
            from pymsgbox import confirm
            print(
                f"[WARNING] Goal not Achieved and only {turn} turn left, run may fail. Please run for fans."
            )
            result = confirm(
                text=f"Goal not Achieved and only {turn} turn left, run may fail. Please run for fans and then close this window.",
                title="Goal not Achieved",
                buttons=["OK"],
            )

            # print("[INFO] Run for fans.")
            # race_found = do_race()

            # if race_found:
            #     continue
            # else:
            #     # If there is no race matching to aptitude, go back and do training instead
            #     click(
            #         img="assets/buttons/back_btn.png",
            #         text="[INFO] Race not found. Proceeding to training.",
            #     )
            #     time.sleep(0.5)

        year_parts = year.split(" ")
        # If Prioritize G1 Race is true, check G1 race every turn
        if (
            PRIORITIZE_G1_RACE
            and year_parts[0] != "Junior"
            and is_racing_available(year)
        ):
            print("[INFO] Prioritizing G1 race.")
            g1_race_found = do_race(PRIORITIZE_G1_RACE)
            if g1_race_found:
                continue
            else:
                # If there is no G1 race, go back and do training
                click(
                    img="assets/buttons/back_btn.png",
                    text="[INFO] G1 race not found. Proceeding to training.",
                )
                time.sleep(0.5)

        # Check training button
        if not go_to_training():
            print("[INFO] Training button is not found.")
            continue

        # Last, do training
        time.sleep(1)
        results_training = check_training()

        best_training = do_something(results_training)
        print(f"[INFO] Best training: {best_training}")
        if best_training == "PRIORITIZE_RACE":
            print("[INFO] Prioritizing race due to insufficient support cards.")

            # Check if stamina training option are unsafe before attempting race
            if check_training_unsafe(results_training, type="stamina"):
                print(
                    f"[INFO] Stamina training option has failure rate > {MAX_FAILURE}%. Skipping race and choosing to rest."
                )
                do_rest()
                continue

            # Check if racing is available (no races in July/August)
            if not is_racing_available(year):
                print(
                    "[INFO] July/August detected. No races available during summer break. Choosing to rest."
                )
                do_rest()
                continue

            race_found = do_race()
            if race_found:
                continue
            else:
                # If no race found, go back to training logic
                print("[INFO] No race found. Returning to training logic.")
                click(
                    img="assets/buttons/back_btn.png",
                    text="[INFO] Race not found. Proceeding to training.",
                )
                time.sleep(0.5)
                # Re-evaluate training without race prioritization
                best_training = do_something_fallback(results_training)
                if best_training:
                    go_to_training()
                    time.sleep(0.5)

                    ### move to guts first if it is wits training
                    if best_training == "wit":
                        print("[INFO] Moving to guts training first for wits training.")
                        click_guts_button()

                    do_train(best_training)
                else:
                    do_rest()
        elif best_training == "rest":
            do_rest()
            continue
        elif best_training:
            go_to_training()
            time.sleep(0.5)

            ### move to guts first if it is wits training
            if best_training == "wit":
                print("[INFO] Moving to guts training first for wits training.")
                click_guts_button()

            do_train(best_training)
        else:
            do_rest()
        time.sleep(1)
