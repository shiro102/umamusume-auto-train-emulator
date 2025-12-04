import subprocess
import json
import time
import re
import socket
import cv2
import numpy as np
from typing import Optional, Tuple, List


class ADBController:
    """ADB controller for phone emulation via Mumu instance"""

    def __init__(self, host: str = "127.0.0.1", port: int = 16384):
        self.host = host
        self.port = port
        self.device_id = None
        self._connect()

    def _connect(self):
        """Connect to ADB device"""
        try:
            # Connect to the ADB server
            subprocess.run(
                ["adb", "connect", f"{self.host}:{self.port}"],
                check=True,
                capture_output=True,
            )

            # Get device list to verify connection
            result = subprocess.run(
                ["adb", "devices"], check=True, capture_output=True, text=True
            )

            devices = result.stdout.strip().split("\n")[1:]  # Skip header
            for device in devices:
                if device.strip() and f"{self.host}:{self.port}" in device:
                    self.device_id = f"{self.host}:{self.port}"
                    print(f"[ADB] Connected to device: {self.device_id}")
                    return True

            print("[ADB] Failed to connect to device")
            return False

        except subprocess.CalledProcessError as e:
            print(f"[ADB] Connection error: {e}")
            return False
        except FileNotFoundError:
            print(
                "[ADB] ADB not found. Please ensure Android SDK is installed and adb is in PATH"
            )
            return False

    def click(self, x: int, y: int, duration: float = 0.175):
        """Perform click at coordinates using ADB"""
        if not self.device_id:
            print("[ADB] No device connected")
            return False

        try:
            # Sleep for duration to allow UI to respond
            if duration > 0:
                time.sleep(duration)

            # Execute click command
            cmd = ["adb", "-s", self.device_id, "shell", "input", "tap", str(x), str(y)]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)

            # print(f"[ADB] Clicked at ({x}, {y})")
            return True

        except subprocess.CalledProcessError as e:
            print(f"[ADB] Click error: {e}")
            return False

    def mouse_down(self, x: int, y: int):
        """Simulate mouse down at coordinates using ADB"""
        if not self.device_id:
            print("[ADB] No device connected")
            return False

        try:
            # Use ADB shell input motionevent DOWN command
            cmd = [
                "adb",
                "-s",
                self.device_id,
                "shell",
                "input",
                "motionevent",
                "DOWN",
                str(x),
                str(y),
            ]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)

            # print(f"[ADB] Mouse down at ({x}, {y})")
            return True

        except subprocess.CalledProcessError as e:
            print(f"[ADB] Mouse down error: {e}")
            return False

    def mouse_up(self, x: int, y: int):
        """Simulate mouse up at coordinates using ADB"""
        if not self.device_id:
            print("[ADB] No device connected")
            return False

        try:
            # Use ADB shell input motionevent UP command
            cmd = [
                "adb",
                "-s",
                self.device_id,
                "shell",
                "input",
                "motionevent",
                "UP",
                str(x),
                str(y),
            ]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)

            # print(f"[ADB] Mouse up at ({x}, {y})")
            return True

        except subprocess.CalledProcessError as e:
            print(f"[ADB] Mouse up error: {e}")
            return False

    def move_to(self, x: int, y: int, duration: float = 0.175):
        """Move to coordinates (ADB doesn't support duration, so we simulate it)"""
        if not self.device_id:
            print("[ADB] No device connected")
            return False

        try:
            # For ADB, we'll just click directly since we can't move without clicking
            # Sleep for duration to simulate movement delay
            if duration > 0:
                time.sleep(duration)
            
            return self.click(x, y, duration=0)  # Click without additional sleep since we already slept

        except Exception as e:
            print(f"[ADB] Move error: {e}")
            return False

    def is_connected(self) -> bool:
        """Check if ADB device is connected"""
        return self.device_id is not None

    def get_screen_size(self) -> Tuple[int, int]:
        """Get screen size using ADB shell command"""
        if not self.device_id:
            return (0, 0)

        try:
            # Get screen size using wm size command
            cmd = ["adb", "-s", self.device_id, "shell", "wm", "size"]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)

            # Parse output like "Physical size: 720x1280"
            output = result.stdout.strip()
            match = re.search(r"(\d+)x(\d+)", output)
            if match:
                width = int(match.group(1))
                height = int(match.group(2))
                return (width, height)
            else:
                print(f"[ADB] Could not parse screen size from: {output}")
                return (0, 0)

        except subprocess.CalledProcessError as e:
            print(f"[ADB] Screen size error: {e}")
            return (0, 0)

    def take_screenshot(self) -> Optional[np.ndarray]:
        """Take screenshot using ADB"""
        if not self.device_id:
            return None

        try:
            # Take screenshot using ADB
            cmd = ["adb", "-s", self.device_id, "exec-out", "screencap -p"]
            result = subprocess.run(cmd, check=True, capture_output=True)

            # Convert bytes to numpy array
            nparr = np.frombuffer(result.stdout, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is not None:
                # Convert BGR to RGB
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                # Screenshot is already in correct portrait orientation (720x1280)
                # height, width = img.shape[:2]
                # print(f"[ADB] Screenshot dimensions: {width}x{height}")

                return img
            else:
                print("[ADB] Failed to decode screenshot")
                return None

        except subprocess.CalledProcessError as e:
            print(f"[ADB] Screenshot error: {e}")
            return None

    def check_screen_resolution(
        self, expected_width: int = 720, expected_height: int = 1280
    ) -> bool:
        """Check if screen resolution matches expected size"""
        width, height = self.get_screen_size()

        if width == 0 or height == 0:
            print("[ADB] Could not get screen size")
            return False

        print(f"[ADB] Screen size: {width}x{height}")

        # Check if resolution matches expected size
        if width == expected_width and height == expected_height:
            print(f"[ADB] ✅ Screen resolution is correct: {width}x{height}")
            return True
        else:
            print(
                f"[ADB] ❌ Screen resolution is incorrect: {width}x{height} (expected: {expected_width}x{expected_height})"
            )
            return False

    def check_screenshot_resolution(
        self, expected_width: int = 720, expected_height: int = 1280
    ) -> bool:
        """Check screenshot resolution using actual screenshot"""
        screenshot = self.take_screenshot()

        if screenshot is None:
            print("[ADB] Could not take screenshot")
            return False

        height, width = screenshot.shape[:2]
        print(f"[ADB] Screenshot size: {width}x{height}")

        # Check if resolution matches expected size
        if width == expected_width and height == expected_height:
            print(f"[ADB] ✅ Screenshot resolution is correct: {width}x{height}")
            return True
        else:
            print(
                f"[ADB] ❌ Screenshot resolution is incorrect: {width}x{height} (expected: {expected_width}x{expected_height})"
            )
            return False


class MumuAutoDetector:
    """Auto-detect and connect to Mumu Player instances"""

    def __init__(self):
        self.adb_binary = "adb"
        self.mumu_ports = list(range(16384, 17409))  # Mumu12 port range
        self.connected_device = None

    def list_devices(self) -> List[dict]:
        """List all available ADB devices"""
        try:
            result = subprocess.run(
                [self.adb_binary, "devices"], check=True, capture_output=True, text=True
            )

            devices = []
            lines = result.stdout.strip().split("\n")[1:]  # Skip header
            for line in lines:
                if line.strip():
                    parts = line.strip().split("\t")
                    if len(parts) == 2:
                        serial, status = parts
                        devices.append(
                            {
                                "serial": serial,
                                "status": status,
                                "port": self._extract_port(serial),
                            }
                        )
            return devices
        except (subprocess.CalledProcessError, FileNotFoundError):
            return []

    def _extract_port(self, serial: str) -> int:
        """Extract port number from serial"""
        try:
            if ":" in serial:
                return int(serial.split(":")[1])
        except (ValueError, IndexError):
            pass
        return 0

    def _is_mumu_port(self, port: int) -> bool:
        """Check if port is in Mumu range"""
        return 16384 <= port <= 17408

    def _is_mumu_device(self, serial: str) -> bool:
        """Check if device is a Mumu instance"""
        port = self._extract_port(serial)
        return self._is_mumu_port(port) and serial.startswith("127.0.0.1:")

    def detect_mumu_instances(self) -> List[dict]:
        """Detect all available Mumu instances"""
        print("[MUMU] Detecting Mumu instances...")

        # First, try to connect to common Mumu ports
        mumu_instances = []

        # Try connecting to known Mumu ports
        for port in [16384, 16385, 16386, 16387, 16388]:  # Common Mumu ports
            try:
                result = subprocess.run(
                    [self.adb_binary, "connect", f"127.0.0.1:{port}"],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                print(
                    f"[MUMU] Tried connecting to 127.0.0.1:{port}: {result.stdout.strip()}"
                )
            except subprocess.CalledProcessError:
                continue

        # Get list of all devices
        devices = self.list_devices()

        # Filter Mumu devices
        for device in devices:
            if self._is_mumu_device(device["serial"]) and device["status"] == "device":
                mumu_instances.append(device)
                print(
                    f"[MUMU] Found Mumu instance: {device['serial']} ({device['status']})"
                )

        return mumu_instances

    def auto_connect_mumu(self) -> Optional[str]:
        """Auto-detect and connect to the best available Mumu instance"""
        print("[MUMU] Starting auto-detection...")

        # Detect Mumu instances
        mumu_instances = self.detect_mumu_instances()

        if not mumu_instances:
            print("[MUMU] No Mumu instances found")
            return None

        # Prefer the first available instance (usually 16384)
        selected_device = mumu_instances[0]
        print(f"[MUMU] Auto-selected Mumu instance: {selected_device['serial']}")

        # Create ADB controller for the selected device
        host, port = selected_device["serial"].split(":")
        self.connected_device = ADBController(host, int(port))

        if self.connected_device.is_connected():
            print(f"[MUMU] Successfully connected to {selected_device['serial']}")
            return selected_device["serial"]
        else:
            print(f"[MUMU] Failed to connect to {selected_device['serial']}")
            return None

    def get_connected_device(self) -> Optional[ADBController]:
        """Get the currently connected device"""
        return self.connected_device

    def test_connection(self, serial: str) -> bool:
        """Test if a specific serial is accessible"""
        try:
            result = subprocess.run(
                [self.adb_binary, "connect", serial],
                check=True,
                capture_output=True,
                text=True,
            )
            return "connected" in result.stdout.lower()
        except subprocess.CalledProcessError:
            return False

    def check_mumu_resolution(
        self, expected_width: int = 720, expected_height: int = 1280
    ) -> bool:
        """Check if connected Mumu device has correct resolution"""
        if not self.connected_device:
            print("[MUMU] No device connected")
            return False

        print(
            f"[MUMU] Checking screen resolution (expected: {expected_width}x{expected_height})..."
        )

        # Check using ADB shell command
        shell_result = self.connected_device.check_screen_resolution(
            expected_width, expected_height
        )

        # Also check using screenshot
        screenshot_result = self.connected_device.check_screenshot_resolution(
            expected_width, expected_height
        )

        return shell_result and screenshot_result


# Global ADB controller instance
_adb_controller = None
_mumu_detector = None


def get_adb_controller() -> Optional[ADBController]:
    """Get or create ADB controller instance"""
    global _adb_controller
    if _adb_controller is None:
        _adb_controller = ADBController()
    return _adb_controller


def get_mumu_detector() -> MumuAutoDetector:
    """Get or create Mumu auto-detector instance"""
    global _mumu_detector
    if _mumu_detector is None:
        _mumu_detector = MumuAutoDetector()
    return _mumu_detector


def auto_connect_mumu() -> Optional[str]:
    """Auto-detect and connect to Mumu Player"""
    detector = get_mumu_detector()
    return detector.auto_connect_mumu()


def check_mumu_resolution(
    expected_width: int = 720, expected_height: int = 1280
) -> bool:
    """Check if Mumu has correct resolution"""
    detector = get_mumu_detector()
    return detector.check_mumu_resolution(expected_width, expected_height)


def adb_click(x: int, y: int, duration: float = 0.175) -> bool:
    """Perform ADB click at coordinates"""
    controller = get_adb_controller()
    if controller and controller.is_connected():
        return controller.click(x, y, duration)
    return False


def adb_move_to(x: int, y: int, duration: float = 0.175) -> bool:
    """Move to coordinates using ADB"""
    controller = get_adb_controller()
    if controller and controller.is_connected():
        return controller.move_to(x, y, duration)
    return False


def adb_mouse_down(x: int, y: int) -> bool:
    """Perform mouse down at coordinates using ADB"""
    controller = get_adb_controller()
    if controller and controller.is_connected():
        return controller.mouse_down(x, y)
    return False


def adb_mouse_up(x: int, y: int) -> bool:
    """Perform mouse up at coordinates using ADB"""
    controller = get_adb_controller()
    if controller and controller.is_connected():
        return controller.mouse_up(x, y)
    return False


def adb_scroll(distance: int, start_x: int = None, start_y: int = None) -> bool:
    """Perform scroll using ADB

    Args:
        distance: Scroll distance (positive for up, negative for down)
        start_x: X coordinate for starting touch point (default: screen center)
        start_y: Y coordinate for starting touch point (default: screen center)
    """
    controller = get_adb_controller()
    if controller and controller.is_connected():
        # Use ADB shell input swipe for scrolling
        try:
            # Get screen size to calculate center
            width, height = controller.get_screen_size()
            if width == 0 or height == 0:
                # Fallback to default phone size
                width, height = 720, 1280

            # Use custom coordinates if provided, otherwise use screen center
            if start_x is None:
                start_x = width // 2
            if start_y is None:
                start_y = height // 2

            # Calculate swipe distance (positive for up, negative for down)
            if distance > 0:
                # Scroll up: swipe from bottom to top
                swipe_start_y = start_y + abs(distance) // 2
                swipe_end_y = start_y - abs(distance) // 2
            else:
                # Scroll down: swipe from top to bottom
                swipe_start_y = start_y - abs(distance) // 2
                swipe_end_y = start_y + abs(distance) // 2

            # Execute swipe command
            cmd = [
                "adb",
                "-s",
                controller.device_id,
                "shell",
                "input",
                "swipe",
                str(start_x),
                str(swipe_start_y),
                str(start_x),
                str(swipe_end_y),
            ]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)

            print(f"[ADB] Scrolled {distance} pixels from ({start_x}, {start_y})")
            return True

        except subprocess.CalledProcessError as e:
            print(f"[ADB] Scroll error: {e}")
            return False
    return False
