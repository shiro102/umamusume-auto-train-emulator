import os
import json
import time
from datetime import datetime

from PIL import Image, ImageEnhance
import mss
import numpy as np

from utils.adb_utils import get_adb_controller

# Load config
try:
    with open("config.json", "r", encoding="utf-8") as file:
        config = json.load(file)
except FileNotFoundError:
    config = {"usePhone": False}

USE_PHONE = config.get("usePhone", True)


def save_debug_image(image: Image.Image, prefix: str = "debug") -> str:
    """
    Save a debug image with timestamp to debug_images directory.

    Args:
        image: PIL Image to save
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

    # Save the image
    image.save(filepath)
    print(f"[DEBUG] Saved debug image: {filepath}")

    return filepath


def enhanced_screenshot(region=(0, 0, 1920, 1080), save_debug=False, name=None) -> Image.Image:
    # Check if usePhone is enabled
    if USE_PHONE:
        # Use ADB screenshot for phone mode
        try:
            controller = get_adb_controller()
            if controller and controller.is_connected():
                # Take full screenshot from phone
                screenshot = controller.take_screenshot()
                
                if screenshot is not None:
                    # Convert numpy array to PIL Image
                    pil_img = Image.fromarray(screenshot)

                    # # Save screenshot to file for debugging
                    # pil_img.save("screenshot-screenshot.png")

                    # Crop to the specified region if not full screen
                    if region != (0, 0, 1920, 1080):
                        # print(f"[DEBUG] Cropping to region: {region}")
                        pil_img = pil_img.crop(
                            (
                                region[0],
                                region[1],
                                region[0] + region[2],
                                region[1] + region[3],
                            )
                        )

                    # Apply enhancements for OCR
                    pil_img = pil_img.resize(
                        (pil_img.width * 2, pil_img.height * 2), Image.BICUBIC
                    )
                    pil_img = pil_img.convert("L")
                    pil_img = ImageEnhance.Contrast(pil_img).enhance(1.5)

                    # Save debug image if requested
                    if save_debug:
                        save_debug_image(pil_img, f"{name}_enhanced_screenshot")
                        time.sleep(1)

                    return pil_img
                else:
                    print(
                        "[WARNING] Could not take ADB screenshot, falling back to desktop"
                    )
            else:
                print("[WARNING] ADB not connected, falling back to desktop screenshot")
        except Exception as e:
            print(f"[WARNING] ADB screenshot failed: {e}, falling back to desktop")

    # Fallback to desktop screenshot
    with mss.mss() as sct:
        monitor = {
            "left": region[0],
            "top": region[1],
            "width": region[2],
            "height": region[3],
        }
        img = sct.grab(monitor)
        img_np = np.array(img)
        img_rgb = img_np[:, :, :3][:, :, ::-1]
        pil_img = Image.fromarray(img_rgb)

    pil_img = pil_img.resize((pil_img.width * 2, pil_img.height * 2), Image.BICUBIC)
    pil_img = pil_img.convert("L")
    pil_img = ImageEnhance.Contrast(pil_img).enhance(1.5)

    # Save debug image if requested
    if save_debug:
        save_debug_image(pil_img, f"{name}_enhanced_screenshot")

    return pil_img


def capture_region(region=(0, 0, 1920, 1080), save_debug=False, name=None) -> Image.Image:
    # Check if usePhone is enabled
    if USE_PHONE:
        # Use ADB screenshot for phone mode
        try:
            controller = get_adb_controller()
            if controller and controller.is_connected():
                # Take full screenshot from phone
                screenshot = controller.take_screenshot()
                if screenshot is not None:
                    # Convert numpy array to PIL Image
                    pil_img = Image.fromarray(screenshot)

                    # Crop to the specified region if not full screen
                    if region != (0, 0, 1920, 1080):
                        pil_img = pil_img.crop(
                            (
                                region[0],
                                region[1],
                                region[0] + region[2],
                                region[1] + region[3],
                            )
                        )

                    if save_debug:
                        save_debug_image(pil_img, f"{name}_capture_region")

                    return pil_img
                else:
                    print(
                        "[WARNING] Could not take ADB screenshot, falling back to desktop"
                    )
            else:
                print("[WARNING] ADB not connected, falling back to desktop screenshot")
        except Exception as e:
            print(f"[WARNING] ADB screenshot failed: {e}, falling back to desktop")

    # Fallback to desktop screenshot
    with mss.mss() as sct:
        monitor = {
            "left": region[0],
            "top": region[1],
            "width": region[2],
            "height": region[3],
        }
        img = sct.grab(monitor)
        img_np = np.array(img)
        img_rgb = img_np[:, :, :3][:, :, ::-1]
        return Image.fromarray(img_rgb)
