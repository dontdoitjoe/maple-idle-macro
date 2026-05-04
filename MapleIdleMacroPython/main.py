#!/usr/bin/env python3
"""
Maple Idle Macro - Python Edition
A macOS automation tool for Maple Idle running on BlueStacks Air emulator.
"""

import sys
import os
import traceback
from pathlib import Path


def _log_dir() -> Path:
    d = Path.home() / "Library" / "Application Support" / "MapleIdleMacro"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _append_launch_log(msg: str):
    log_path = _log_dir() / "launch.log"
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(msg)
            if not msg.endswith("\n"):
                f.write("\n")
    except OSError:
        pass


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _ensure_packaged_path_has_common_bin_dirs():
    """Make common Homebrew/local bin dirs visible to packaged app subprocesses."""
    existing = os.environ.get("PATH", "")
    extras = ["/opt/homebrew/bin", "/usr/local/bin"]
    parts = existing.split(":") if existing else []
    for d in extras:
        if d not in parts:
            parts.append(d)
    os.environ["PATH"] = ":".join(parts)


def main():
    from PyQt6.QtWidgets import QApplication, QMessageBox
    from src.app import MainWindow
    from src.utils.permissions import check_permissions

    app = None
    try:
        _ensure_packaged_path_has_common_bin_dirs()
        app = QApplication(sys.argv)
        app.setApplicationName("Maple Idle Macro")
        app.setOrganizationName("MapleIdleMacro")
        app.setOrganizationDomain("mapleidlemacro.local")

        app.setStyle("Fusion")

        if not check_permissions():
            print(
                "Warning: Accessibility may not be granted. "
                "Clicks and keys may not work until you allow the app in System Settings."
            )

        window = MainWindow()
        window.show()

        sys.exit(app.exec())
    except Exception:
        tb = traceback.format_exc()
        _append_launch_log(tb)
        print(tb, file=sys.stderr)
        try:
            qa = app or QApplication.instance()
            if qa is None:
                qa = QApplication(sys.argv)
            QMessageBox.critical(
                None,
                "Maple Idle Macro failed to start",
                "The app crashed on startup. Details were written to:\n\n"
                f"{_log_dir() / 'launch.log'}\n\n"
                "Try running from Terminal with:\n"
                "  python3 main.py\n"
                "to see the full error.",
            )
        except Exception:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()
