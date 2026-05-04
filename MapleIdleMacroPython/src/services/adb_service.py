"""ADB helper service for device discovery and input commands."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


class AdbError(RuntimeError):
    """Raised when an adb command cannot be completed."""


@dataclass
class AdbDevice:
    serial: str
    state: str


class AdbService:
    """Wraps adb command execution and key/tap helpers."""

    KEY_MAP: Dict[str, str] = {
        "enter": "KEYCODE_ENTER",
        "space": "KEYCODE_SPACE",
        "left": "KEYCODE_DPAD_LEFT",
        "right": "KEYCODE_DPAD_RIGHT",
        "up": "KEYCODE_DPAD_UP",
        "down": "KEYCODE_DPAD_DOWN",
        "escape": "KEYCODE_ESCAPE",
        "esc": "KEYCODE_ESCAPE",
        "backspace": "KEYCODE_DEL",
        "tab": "KEYCODE_TAB",
        "back": "KEYCODE_BACK",
        "home": "KEYCODE_HOME",
        "menu": "KEYCODE_MENU",
        "volumeup": "KEYCODE_VOLUME_UP",
        "volumedown": "KEYCODE_VOLUME_DOWN",
    }

    def __init__(self, adb_path: Optional[str] = None):
        self.adb_path = adb_path or self._resolve_adb_path()

    def _resolve_adb_path(self) -> str:
        candidates = [
            shutil.which("adb"),
            "/opt/homebrew/bin/adb",
            "/usr/local/bin/adb",
        ]
        for candidate in candidates:
            if candidate:
                return candidate
        return "adb"

    def _run(self, args: List[str], timeout: int = 10) -> subprocess.CompletedProcess:
        try:
            return subprocess.run(
                [self.adb_path, *args],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except FileNotFoundError as e:
            raise AdbError(
                "adb not found. Install Android Platform Tools and ensure adb is in PATH."
            ) from e
        except subprocess.TimeoutExpired as e:
            raise AdbError(f"adb command timed out: {' '.join(args)}") from e

    def devices(self) -> List[AdbDevice]:
        result = self._run(["devices"], timeout=8)
        if result.returncode != 0:
            raise AdbError(result.stderr.strip() or "Failed to run 'adb devices'.")

        rows = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line or line.startswith("List of devices attached"):
                continue
            parts = line.split()
            if len(parts) >= 2:
                rows.append(AdbDevice(serial=parts[0], state=parts[1]))
        return rows

    def resolve_device(
        self,
        serial_override: Optional[str] = None,
        auto_select: bool = True,
    ) -> str:
        if serial_override:
            return serial_override.strip()

        if not auto_select:
            raise AdbError("No ADB device selected. Set a serial or enable auto-select.")

        devices = self.devices()
        online = [d for d in devices if d.state == "device"]
        if not online:
            if any(d.state == "unauthorized" for d in devices):
                raise AdbError(
                    "ADB device is unauthorized. Accept the authorization dialog in BlueStacks."
                )
            raise AdbError("No online ADB device found. Start BlueStacks and enable ADB.")
        return online[0].serial

    def status(
        self,
        serial_override: Optional[str] = None,
        auto_select: bool = True,
    ) -> Tuple[bool, str]:
        try:
            serial = self.resolve_device(serial_override, auto_select)
            return True, f"ADB Connected ({serial})"
        except AdbError as e:
            return False, f"ADB: {e}"

    def tap(self, x: int, y: int, device_serial: str):
        result = self._run(
            ["-s", device_serial, "shell", "input", "tap", str(int(x)), str(int(y))],
            timeout=10,
        )
        if result.returncode != 0:
            raise AdbError(result.stderr.strip() or "Failed to send ADB tap command.")

    def keyevent(self, key_name: str, hold_seconds: float, device_serial: str):
        code = self.to_android_keycode(key_name)
        cmd = ["-s", device_serial, "shell", "input", "keyevent"]
        if hold_seconds > 0:
            cmd.append("--longpress")
        cmd.append(code)
        result = self._run(cmd, timeout=10)
        if result.returncode != 0:
            raise AdbError(
                result.stderr.strip() or f"Failed to send ADB keyevent ({code})."
            )

    def to_android_keycode(self, key_name: str) -> str:
        key = (key_name or "").strip().lower()
        if not key:
            raise AdbError("Key name is empty.")

        if key in self.KEY_MAP:
            return self.KEY_MAP[key]

        if len(key) == 1 and key.isalpha():
            return f"KEYCODE_{key.upper()}"
        if len(key) == 1 and key.isdigit():
            return f"KEYCODE_{key}"

        if key.startswith("keycode_"):
            return key.upper()

        raise AdbError(
            f"Unsupported key '{key_name}'. Use common keys like space/enter/arrows, "
            "single letters/digits, or explicit KEYCODE_*."
        )
