"""Configuration management for the macro app."""

import json
from pathlib import Path
from typing import Optional


class Config:
    """Application configuration settings."""

    def __init__(self):
        self.loop_enabled: bool = True
        self.default_delay: float = 1.0
        self.click_duration: float = 0.05
        self.focus_bluestacks_before_action: bool = True
        self.input_backend: str = "desktop"
        self.adb_auto_select_device: bool = True
        self.adb_device_serial: str = ""
        self.auto_start_on_launch: bool = False
        self.show_notifications: bool = True
        self._config_dir: Path = Path.home() / "Library" / "Application Support" / "MapleIdleMacro"
        self._config_file: Path = self._config_dir / "config.json"
        self._config_dir.mkdir(parents=True, exist_ok=True)

    @property
    def config_dir(self) -> Path:
        return self._config_dir

    @property
    def actions_file(self) -> Path:
        return self._config_dir / "actions.json"

    def save(self):
        """Save configuration to disk."""
        data = {
            "loop_enabled": self.loop_enabled,
            "default_delay": self.default_delay,
            "click_duration": self.click_duration,
            "focus_bluestacks_before_action": self.focus_bluestacks_before_action,
            "input_backend": self.input_backend,
            "adb_auto_select_device": self.adb_auto_select_device,
            "adb_device_serial": self.adb_device_serial,
            "auto_start_on_launch": self.auto_start_on_launch,
            "show_notifications": self.show_notifications,
        }
        with open(self._config_file, 'w') as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls) -> 'Config':
        """Load configuration from disk."""
        config = cls()
        if config._config_file.exists():
            try:
                with open(config._config_file, 'r') as f:
                    data = json.load(f)
                config.loop_enabled = data.get("loop_enabled", True)
                config.default_delay = data.get("default_delay", 1.0)
                config.click_duration = data.get("click_duration", 0.05)
                config.focus_bluestacks_before_action = data.get(
                    "focus_bluestacks_before_action", True
                )
                config.input_backend = data.get("input_backend", "desktop")
                if config.input_backend not in ("desktop", "adb"):
                    config.input_backend = "desktop"
                config.adb_auto_select_device = data.get("adb_auto_select_device", True)
                config.adb_device_serial = data.get("adb_device_serial", "")
                config.auto_start_on_launch = data.get("auto_start_on_launch", False)
                config.show_notifications = data.get("show_notifications", True)
            except (json.JSONDecodeError, IOError):
                pass
        return config


_config_instance: Optional[Config] = None


def get_config() -> Config:
    """Get the global config instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config.load()
    return _config_instance
