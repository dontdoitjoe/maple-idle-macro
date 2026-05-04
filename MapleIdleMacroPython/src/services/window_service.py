"""Service for detecting and tracking BlueStacks window."""

import subprocess
from typing import Optional, Dict, List
from dataclasses import dataclass


@dataclass
class WindowInfo:
    """Information about a detected window."""
    window_id: int
    owner_name: str
    window_name: str
    bounds: Dict[str, float]
    
    @property
    def x(self) -> float:
        return self.bounds.get('X', 0)
    
    @property
    def y(self) -> float:
        return self.bounds.get('Y', 0)
    
    @property
    def width(self) -> float:
        return self.bounds.get('Width', 0)
    
    @property
    def height(self) -> float:
        return self.bounds.get('Height', 0)


class WindowService:
    """Service for finding and tracking the BlueStacks window."""
    
    BLUESTACKS_IDENTIFIERS = [
        "BlueStacks",
        "BlueStacks Air",
        "HD-Player",
        "Bluestacks"
    ]
    
    def __init__(self):
        self._current_window: Optional[WindowInfo] = None
    
    def find_bluestacks_window(self) -> Optional[WindowInfo]:
        """Find the BlueStacks window and return its info."""
        try:
            from Quartz import (
                CGWindowListCopyWindowInfo,
                kCGWindowListOptionOnScreenOnly,
                kCGWindowListExcludeDesktopElements,
                kCGNullWindowID
            )
            
            options = kCGWindowListOptionOnScreenOnly | kCGWindowListExcludeDesktopElements
            windows = CGWindowListCopyWindowInfo(options, kCGNullWindowID)
            
            if not windows:
                return None
            
            for window in windows:
                owner_name = window.get('kCGWindowOwnerName', '')
                
                is_bluestacks = any(
                    identifier.lower() in owner_name.lower()
                    for identifier in self.BLUESTACKS_IDENTIFIERS
                )
                
                if is_bluestacks:
                    bounds = window.get('kCGWindowBounds', {})
                    width = bounds.get('Width', 0)
                    height = bounds.get('Height', 0)
                    
                    if width > 100 and height > 100:
                        self._current_window = WindowInfo(
                            window_id=window.get('kCGWindowNumber', 0),
                            owner_name=owner_name,
                            window_name=window.get('kCGWindowName', ''),
                            bounds=bounds
                        )
                        return self._current_window
            
            return None
            
        except ImportError:
            print("Error: pyobjc-framework-Quartz is required")
            return None
        except Exception as e:
            print(f"Error finding BlueStacks window: {e}")
            return None
    
    def get_all_windows(self) -> List[WindowInfo]:
        """Get all visible windows."""
        windows_list = []
        
        try:
            from Quartz import (
                CGWindowListCopyWindowInfo,
                kCGWindowListOptionOnScreenOnly,
                kCGWindowListExcludeDesktopElements,
                kCGNullWindowID
            )
            
            options = kCGWindowListOptionOnScreenOnly | kCGWindowListExcludeDesktopElements
            windows = CGWindowListCopyWindowInfo(options, kCGNullWindowID)
            
            if not windows:
                return windows_list
            
            for window in windows:
                bounds = window.get('kCGWindowBounds', {})
                width = bounds.get('Width', 0)
                height = bounds.get('Height', 0)
                
                if width > 50 and height > 50:
                    windows_list.append(WindowInfo(
                        window_id=window.get('kCGWindowNumber', 0),
                        owner_name=window.get('kCGWindowOwnerName', ''),
                        window_name=window.get('kCGWindowName', ''),
                        bounds=bounds
                    ))
            
        except Exception as e:
            print(f"Error getting windows: {e}")
        
        return windows_list
    
    def get_window_bounds(self, window_id: int) -> Optional[Dict[str, float]]:
        """Get current bounds of a specific window."""
        try:
            from Quartz import (
                CGWindowListCopyWindowInfo,
                kCGWindowListOptionIncludingWindow,
                kCGNullWindowID
            )
            
            windows = CGWindowListCopyWindowInfo(
                kCGWindowListOptionIncludingWindow,
                window_id
            )
            
            if windows and len(windows) > 0:
                return windows[0].get('kCGWindowBounds', {})
            
        except Exception as e:
            print(f"Error getting window bounds: {e}")
        
        return None
    
    @property
    def current_window(self) -> Optional[WindowInfo]:
        """Get the currently tracked window."""
        return self._current_window
    
    def refresh(self) -> Optional[WindowInfo]:
        """Refresh the BlueStacks window detection."""
        return self.find_bluestacks_window()

    def activate_bluestacks(self) -> bool:
        """
        Bring BlueStacks to the foreground so keyboard/mouse events reach it.
        Tries AppKit first, then AppleScript (may prompt for Automation once).
        """
        try:
            from AppKit import NSWorkspace, NSApplicationActivateIgnoringOtherApps

            ws = NSWorkspace.sharedWorkspace()
            flags = NSApplicationActivateIgnoringOtherApps
            for ra in ws.runningApplications():
                name = (ra.localizedName() or "") or ""
                bid = (ra.bundleIdentifier() or "") or ""
                name_l = name.lower()
                bid_l = bid.lower()
                if any(
                    ident.lower() in name_l for ident in self.BLUESTACKS_IDENTIFIERS
                ) or "bluestacks" in bid_l or "hd-player" in bid_l:
                    if ra.activateWithOptions_(flags):
                        return True
        except Exception:
            pass
        return self._activate_bluestacks_applescript()

    def _activate_bluestacks_applescript(self) -> bool:
        for app_name in ("BlueStacks Air", "BlueStacks", "HD-Player"):
            script = f'tell application "{app_name}" to activate'
            try:
                r = subprocess.run(
                    ["osascript", "-e", script],
                    capture_output=True,
                    timeout=10,
                )
                if r.returncode == 0:
                    return True
            except Exception:
                continue
        return False
