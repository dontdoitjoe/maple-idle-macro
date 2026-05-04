"""Input backend abstraction for desktop and ADB modes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from .adb_service import AdbError, AdbService
from .click_service import ClickService
from .window_service import WindowService


@dataclass
class InputStatus:
    connected: bool
    label: str
    details: str = ""


class InputBackendBase:
    backend_id = "desktop"
    requires_window_for_click = True

    def get_status(self) -> InputStatus:
        raise NotImplementedError

    def click(self, x: int, y: int, window_bounds: Optional[Dict[str, float]] = None):
        raise NotImplementedError

    def press_key(self, key_name: str, hold_seconds: float):
        raise NotImplementedError


class DesktopInputBackend(InputBackendBase):
    backend_id = "desktop"
    requires_window_for_click = True

    def __init__(
        self,
        click_service: ClickService,
        window_service: WindowService,
        focus_before_action: bool,
    ):
        self.click_service = click_service
        self.window_service = window_service
        self.focus_before_action = focus_before_action

    def _prepare_foreground(self):
        if self.focus_before_action:
            self.window_service.activate_bluestacks()

    def get_status(self) -> InputStatus:
        window = self.window_service.find_bluestacks_window()
        if not window:
            return InputStatus(False, "BlueStacks: Not Found", "Window: --")
        return InputStatus(
            True,
            "BlueStacks: Connected",
            f"Window: {int(window.width)} x {int(window.height)}",
        )

    def click(self, x: int, y: int, window_bounds: Optional[Dict[str, float]] = None):
        self._prepare_foreground()
        self.click_service.click(x, y, window_bounds)

    def press_key(self, key_name: str, hold_seconds: float):
        self._prepare_foreground()
        self.click_service.press_key(key_name, hold_seconds)


class AdbInputBackend(InputBackendBase):
    backend_id = "adb"
    requires_window_for_click = False

    def __init__(
        self,
        adb_service: AdbService,
        auto_select_device: bool = True,
        device_serial: str = "",
    ):
        self.adb_service = adb_service
        self.auto_select_device = auto_select_device
        self.device_serial = (device_serial or "").strip()

    def _current_serial(self) -> str:
        return self.adb_service.resolve_device(
            serial_override=self.device_serial or None,
            auto_select=self.auto_select_device,
        )

    def get_status(self) -> InputStatus:
        ok, label = self.adb_service.status(
            serial_override=self.device_serial or None,
            auto_select=self.auto_select_device,
        )
        details = (
            "Mode: Android Debug Bridge"
            if ok
            else "Install Android Platform Tools and ensure BlueStacks ADB is available."
        )
        return InputStatus(ok, label, details)

    def click(self, x: int, y: int, window_bounds: Optional[Dict[str, float]] = None):
        _ = window_bounds
        serial = self._current_serial()
        self.adb_service.tap(x, y, serial)

    def press_key(self, key_name: str, hold_seconds: float):
        serial = self._current_serial()
        self.adb_service.keyevent(key_name, hold_seconds, serial)

