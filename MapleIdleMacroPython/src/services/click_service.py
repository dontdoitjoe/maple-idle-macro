"""Service for simulating mouse clicks."""

import time
from typing import Optional, Dict, Tuple
import pyautogui


pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.01


class ClickService:
    """Service for simulating mouse clicks and movements."""
    
    def __init__(self, click_duration: float = 0.05):
        self.click_duration = click_duration
    
    def click(
        self,
        x: int,
        y: int,
        window_bounds: Optional[Dict[str, float]] = None
    ):
        """
        Perform a click at the specified coordinates.
        
        Args:
            x: X coordinate (relative to window if bounds provided)
            y: Y coordinate (relative to window if bounds provided)
            window_bounds: Optional window bounds dict with X, Y keys
        """
        if window_bounds:
            screen_x = window_bounds.get('X', 0) + x
            screen_y = window_bounds.get('Y', 0) + y
        else:
            screen_x = x
            screen_y = y
        
        pyautogui.click(screen_x, screen_y, _pause=False)
    
    def click_with_duration(
        self,
        x: int,
        y: int,
        window_bounds: Optional[Dict[str, float]] = None,
        duration: Optional[float] = None
    ):
        """
        Perform a click with specified hold duration.
        
        Args:
            x: X coordinate
            y: Y coordinate
            window_bounds: Optional window bounds
            duration: How long to hold the click (defaults to self.click_duration)
        """
        if duration is None:
            duration = self.click_duration
        
        if window_bounds:
            screen_x = window_bounds.get('X', 0) + x
            screen_y = window_bounds.get('Y', 0) + y
        else:
            screen_x = x
            screen_y = y
        
        pyautogui.moveTo(screen_x, screen_y, _pause=False)
        pyautogui.mouseDown(_pause=False)
        time.sleep(duration)
        pyautogui.mouseUp(_pause=False)
    
    def double_click(
        self,
        x: int,
        y: int,
        window_bounds: Optional[Dict[str, float]] = None
    ):
        """Perform a double click."""
        if window_bounds:
            screen_x = window_bounds.get('X', 0) + x
            screen_y = window_bounds.get('Y', 0) + y
        else:
            screen_x = x
            screen_y = y
        
        pyautogui.doubleClick(screen_x, screen_y, _pause=False)
    
    def right_click(
        self,
        x: int,
        y: int,
        window_bounds: Optional[Dict[str, float]] = None
    ):
        """Perform a right click."""
        if window_bounds:
            screen_x = window_bounds.get('X', 0) + x
            screen_y = window_bounds.get('Y', 0) + y
        else:
            screen_x = x
            screen_y = y
        
        pyautogui.rightClick(screen_x, screen_y, _pause=False)
    
    def move_to(
        self,
        x: int,
        y: int,
        window_bounds: Optional[Dict[str, float]] = None,
        duration: float = 0
    ):
        """Move the mouse to a position."""
        if window_bounds:
            screen_x = window_bounds.get('X', 0) + x
            screen_y = window_bounds.get('Y', 0) + y
        else:
            screen_x = x
            screen_y = y
        
        pyautogui.moveTo(screen_x, screen_y, duration=duration, _pause=False)
    
    def drag(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        window_bounds: Optional[Dict[str, float]] = None,
        duration: float = 0.5
    ):
        """Drag from one position to another."""
        if window_bounds:
            offset_x = window_bounds.get('X', 0)
            offset_y = window_bounds.get('Y', 0)
            start_x += offset_x
            start_y += offset_y
            end_x += offset_x
            end_y += offset_y
        
        pyautogui.moveTo(start_x, start_y, _pause=False)
        pyautogui.drag(
            end_x - start_x,
            end_y - start_y,
            duration=duration,
            _pause=False
        )
    
    def scroll(
        self,
        clicks: int,
        x: Optional[int] = None,
        y: Optional[int] = None,
        window_bounds: Optional[Dict[str, float]] = None
    ):
        """
        Scroll the mouse wheel.
        
        Args:
            clicks: Number of scroll clicks (positive = up, negative = down)
            x: Optional X position to scroll at
            y: Optional Y position to scroll at
            window_bounds: Optional window bounds
        """
        if x is not None and y is not None:
            if window_bounds:
                x += window_bounds.get('X', 0)
                y += window_bounds.get('Y', 0)
            pyautogui.moveTo(x, y, _pause=False)
        
        pyautogui.scroll(clicks, _pause=False)
    
    def press_key(self, key: str, hold_seconds: float = 0.0):
        """
        Send a key event using PyAutoGUI key names (e.g. space, enter, left, a).
        If hold_seconds > 0, holds the key down for that duration.
        """
        key = (key or "").strip()
        if not key:
            return
        if hold_seconds > 0:
            pyautogui.keyDown(key, _pause=False)
            time.sleep(hold_seconds)
            pyautogui.keyUp(key, _pause=False)
        else:
            pyautogui.press(key, _pause=False)

    def get_position(self) -> Tuple[int, int]:
        """Get the current mouse position."""
        return pyautogui.position()
    
    @staticmethod
    def get_screen_size() -> Tuple[int, int]:
        """Get the screen size."""
        return pyautogui.size()
