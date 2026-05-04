"""Macro execution engine that coordinates all services."""

import time
import threading
from typing import Optional

from .services.adb_service import AdbError
from .services.input_backend import InputBackendBase
from .services.window_service import WindowService
from .models.action import ActionManager, ActionType
from .utils.config import Config


class MacroEngine:
    """Engine for executing macro actions."""

    def __init__(
        self,
        window_service: WindowService,
        input_backend: InputBackendBase,
        action_manager: ActionManager,
        config: Config
    ):
        self.window_service = window_service
        self.input_backend = input_backend
        self.action_manager = action_manager
        self.config = config

        self._is_running = False
        self._is_paused = False
        self._current_action_index = 0
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()

        self.loop_enabled = config.loop_enabled
        self.action_delay = config.default_delay

        self.on_action_started = None
        self.on_action_completed = None
        self.on_macro_completed = None
        self.on_error = None

    @property
    def is_running(self) -> bool:
        return self._is_running

    @property
    def is_paused(self) -> bool:
        return self._is_paused

    @property
    def current_action_index(self) -> int:
        return self._current_action_index

    def start(self):
        """Start the macro execution."""
        if self._is_running:
            return

        if not self.action_manager.actions:
            return

        self._is_running = True
        self._is_paused = False
        self._current_action_index = 0
        self._stop_event.clear()
        self._pause_event.clear()

        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the macro execution."""
        self._stop_event.set()
        self._pause_event.set()
        self._is_running = False
        self._is_paused = False

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)

        self._current_action_index = 0

    def pause(self):
        """Pause the macro execution."""
        if self._is_running and not self._is_paused:
            self._is_paused = True
            self._pause_event.clear()

    def resume(self):
        """Resume the macro execution."""
        if self._is_running and self._is_paused:
            self._is_paused = False
            self._pause_event.set()

    def set_input_backend(self, backend: InputBackendBase):
        """Update the active input backend at runtime."""
        self.input_backend = backend

    def _run_loop(self):
        """Main execution loop."""
        try:
            while not self._stop_event.is_set():
                while self._is_paused and not self._stop_event.is_set():
                    self._pause_event.wait(timeout=0.1)

                if self._stop_event.is_set():
                    break

                if self._current_action_index >= len(self.action_manager.actions):
                    if self.loop_enabled:
                        self._current_action_index = 0
                    else:
                        break

                action = self.action_manager.actions[self._current_action_index]

                if action.enabled:
                    if self.on_action_started:
                        self.on_action_started(self._current_action_index, action)

                    try:
                        self._execute_action(action)
                    except AdbError as e:
                        if self.on_error:
                            self.on_error(str(e))
                        self._stop_event.set()
                        self._pause_event.set()
                        self._is_running = False
                        self._is_paused = False
                        break

                    if self.on_action_completed:
                        self.on_action_completed(self._current_action_index, action)

                self._current_action_index += 1

                if not self._stop_event.is_set():
                    time.sleep(self.action_delay)

            if self.on_macro_completed:
                self.on_macro_completed()

        except Exception as e:
            if self.on_error:
                self.on_error(str(e))
        finally:
            self._is_running = False
            self._is_paused = False

    def _execute_action(self, action):
        """Execute a single action."""
        window = self.window_service.current_window

        if action.action_type == ActionType.DELAY:
            self._execute_delay(action)
            return

        if action.action_type == ActionType.FIXED_CLICK:
            if self.input_backend.requires_window_for_click and not window:
                return
            self._execute_fixed_click(action, window)
            return

        if action.action_type == ActionType.KEY_PRESS:
            self.input_backend.press_key(
                action.key_name,
                action.key_hold_seconds,
            )
            return

    def _execute_fixed_click(self, action, window):
        """Execute a fixed position click."""
        bounds = window.bounds if window else None
        self.input_backend.click(
            action.click_x,
            action.click_y,
            bounds
        )

    def _execute_delay(self, action):
        """Execute a delay action."""
        remaining = action.delay_seconds
        interval = 0.1

        while remaining > 0 and not self._stop_event.is_set():
            while self._is_paused and not self._stop_event.is_set():
                self._pause_event.wait(timeout=0.1)

            if self._stop_event.is_set():
                break

            sleep_time = min(interval, remaining)
            time.sleep(sleep_time)
            remaining -= sleep_time
