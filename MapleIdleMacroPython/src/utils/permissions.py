"""macOS permission handling for accessibility (synthetic input)."""

import subprocess
import webbrowser


def check_accessibility_permission() -> bool:
    """Check if accessibility permission is granted."""
    try:
        from Quartz import AXIsProcessTrusted
        return AXIsProcessTrusted()
    except ImportError:
        try:
            result = subprocess.run(
                ['osascript', '-e', 'tell application "System Events" to return true'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False


def check_permissions() -> bool:
    """Return True if accessibility is granted (required for clicks and keys)."""
    return check_accessibility_permission()


def request_accessibility():
    """Open System Settings to Accessibility preferences."""
    webbrowser.open(
        "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"
    )


def get_permission_status() -> bool:
    """True if Accessibility is granted."""
    return check_accessibility_permission()
