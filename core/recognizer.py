import json

import cv2
import numpy as np
from PIL import ImageGrab, ImageStat

from utils.screenshot import capture_region
from utils.adb_utils import get_adb_controller
import os
from datetime import datetime
from PIL import Image
import time

def save_debug_image(image, prefix: str = "debug") -> str:
    """
    Save a debug image with timestamp to debug_images directory.

    Args:
        image: PIL Image or numpy array to save
        prefix: Prefix for the filename

    Returns:
        str: Path to the saved debug image
    """
    # Create debug_images directory if it doesn't exist
    debug_dir = "debug_images"
    if not os.path.exists(debug_dir):
        os.makedirs(debug_dir)

    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.png"
    filepath = os.path.join(debug_dir, filename)

    # Convert numpy array to PIL Image if needed
    if isinstance(image, np.ndarray):
        # Convert BGR to RGB if it's a color image
        if len(image.shape) == 3 and image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)

    # Save the image
    image.save(filepath)
    print(f"[DEBUG] Saved debug image: {filepath}")

    return filepath


def match_template(template_path, secondary_templates={}, region=None, threshold=0.85, debug=False, name=None):
    # Check if usePhone is enabled
    try:
        with open("config.json", "r", encoding="utf-8") as file:
            config = json.load(file)
    except FileNotFoundError:
        config = {"usePhone": False}

    USE_PHONE = config.get("usePhone", True)

    # if USE_PHONE:
    #     # Use ADB screenshot for phone mode
    #     try:
    #         controller = get_adb_controller()
    #         if controller and controller.is_connected():
    #             # Take full screenshot from phone
    #             screen = controller.take_screenshot()

    #             if screen is not None:
    #                 # Convert RGB to BGR for OpenCV
    #                 screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)

    #                 # Extract region if specified
    #                 if region:
    #                     x, y, w, h = region
    #                     screen = screen[y : y + h, x : x + w]
    #                     # Load template
    #                 template = cv2.imread(
    #                     template_path, cv2.IMREAD_COLOR
    #                 )  # safe default

    #                 if template.shape[2] == 4:
    #                     template = cv2.cvtColor(template, cv2.COLOR_BGRA2BGR)

    #                 if debug:
    #                     print(f"[DEBUG] Template loaded: {template_path}")
    #                     print(f"[DEBUG] Template size: {template.shape}")
    #                     print(f"[DEBUG] Screen size: {screen.shape}")

    #                 result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)

    #                 # Get confidence levels for debugging
    #                 if debug:
    #                     min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    #                     print(f"[DEBUG] Max confidence: {max_val:.4f}")
    #                     print(f"[DEBUG] Min confidence: {min_val:.4f}")
    #                     print(f"[DEBUG] Threshold: {threshold}")

    #                 loc = np.where(result >= threshold)
    #                 h, w = template.shape[:2]
    #                 boxes = [(x, y, w, h) for (x, y) in zip(*loc[::-1])]

    #                 if debug:
    #                     print(f"[DEBUG] Found {len(boxes)} matches above threshold")
    #                     for i, (x, y, w, h) in enumerate(boxes):
    #                         print(
    #                             f"[DEBUG] Match {i+1}: ({x}, {y}) with size ({w}, {h})"
    #                         )

    #                 return deduplicate_boxes(boxes)
    #             else:
    #                 print(
    #                     "[WARNING] Could not take ADB screenshot, falling back to desktop"
    #                 )
    #         else:
    #             print("[WARNING] ADB not connected, falling back to desktop screenshot")
    #     except Exception as e:
    #         print(f"[WARNING] ADB screenshot failed: {e}, falling back to desktop")

    # Fallback to desktop screenshot
    # Get screenshot
    if region:
        if USE_PHONE:
            controller = get_adb_controller()
            if controller and controller.is_connected():
                # Take full screenshot from phone
                screen = controller.take_screenshot()
                x, y, w, h = region
                screen = screen[y : y + h, x : x + w]
        else:
            screen = np.array(ImageGrab.grab(bbox=region))  # (left, top, right, bottom)
    else:
        if USE_PHONE:
            controller = get_adb_controller()
            if controller and controller.is_connected():
                # Take full screenshot from phone
                screen = controller.take_screenshot()
        else:
            screen = np.array(ImageGrab.grab())

    screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)

    # Match primary template
    template = cv2.imread(template_path, cv2.IMREAD_COLOR)  # safe default
    if template.shape[2] == 4:
        template = cv2.cvtColor(template, cv2.COLOR_BGRA2BGR)
    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)

    loc = np.where(result >= threshold)

    h, w = template.shape[:2]
    primary_boxes = deduplicate_boxes([(x, y, w, h) for (x, y) in zip(*loc[::-1])])

    # Use cv2.minMaxLoc to get max confidence safely from the result matrix
    if debug:
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        print(f"[DEBUG] Max confidence for {name}: {max_val:.4f}")
        print(f"[DEBUG] Min confidence for {name}: {min_val:.4f}")
        vis = screen.copy()
        for (x, y) in zip(*loc[::-1]):
            cv2.rectangle(vis, (x, y), (x + w, y + h), (0, 255, 0), 2)
        save_debug_image(
            Image.fromarray(cv2.cvtColor(vis, cv2.COLOR_BGR2RGB)),
            f"{name}_template_search",
        )

    # Match secondary templates
    secondary_dicts = {}
    for secondary_name, secondary_path in secondary_templates.items():
        time.sleep(0.5) 
        secondary_template = cv2.imread(secondary_path, cv2.IMREAD_COLOR)
        if secondary_template.shape[2] == 4:
            secondary_template = cv2.cvtColor(secondary_template, cv2.COLOR_BGRA2BGR)
        result = cv2.matchTemplate(screen, secondary_template, cv2.TM_CCOEFF_NORMED)

        if debug:
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            print(f"[DEBUG] Max confidence for {secondary_name}: {max_val:.4f}")
            print(f"[DEBUG] Min confidence for {secondary_name}: {min_val:.4f}")
        
        if secondary_name == "spirit":
            loc = np.where(result >= 0.73)
        else:
            loc = np.where(result >= 0.65)

        h, w = secondary_template.shape[:2]
        secondary_dicts[secondary_name] = deduplicate_boxes([(x, y, w, h) for (x, y) in zip(*loc[::-1])])

    return {
        "primary": primary_boxes,
        "secondary": secondary_dicts,
    }


def deduplicate_boxes(boxes, min_dist=5):
    filtered = []
    for x, y, w, h in boxes:
        cx, cy = x + w // 2, y + h // 2
        if all(
            abs(cx - (fx + fw // 2)) > min_dist or abs(cy - (fy + fh // 2)) > min_dist
            for fx, fy, fw, fh in filtered
        ):
            filtered.append((x, y, w, h))
    return filtered


def is_infirmary_active(REGION):
    screenshot = capture_region(REGION)
    grayscale = screenshot.convert("L")
    stat = ImageStat.Stat(grayscale)
    avg_brightness = stat.mean[0]

    # print(f"[DEBUG] Avg brightness: {avg_brightness}")

    # Treshold infirmary btn
    return avg_brightness > 150
