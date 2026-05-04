"""Main application window."""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QStatusBar, QLabel, QFrame, QMessageBox
)
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QAction

from .services.adb_service import AdbService
from .services.input_backend import AdbInputBackend, DesktopInputBackend
from .services.window_service import WindowService
from .services.click_service import ClickService
from .models.action import ActionManager
from .utils.config import get_config
from .utils.permissions import get_permission_status, request_accessibility
from .views.control_panel import ControlPanel
from .views.action_editor import ActionEditor
from .views.settings_dialog import SettingsDialog
from .macro_engine import MacroEngine


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()

        self.config = get_config()

        self.window_service = WindowService()
        self.click_service = ClickService(self.config.click_duration)
        self.adb_service = AdbService()
        self.input_backend = self.create_input_backend()

        self.action_manager = ActionManager(self.config.actions_file)

        self.macro_engine = MacroEngine(
            window_service=self.window_service,
            input_backend=self.input_backend,
            action_manager=self.action_manager,
            config=self.config
        )

        self.setup_ui()
        self.setup_menu()
        self.setup_status_bar()
        self.setup_timers()

        self.check_permissions()

    def setup_ui(self):
        """Set up the main UI."""
        self.setWindowTitle("Maple Idle Macro")
        self.setMinimumSize(800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        self.control_panel = ControlPanel(
            macro_engine=self.macro_engine,
            window_service=self.window_service,
            click_service=self.click_service,
            input_backend=self.input_backend,
            config=self.config,
            refresh_status_callback=self.check_connection_status,
            mode_change_callback=self.on_control_panel_mode_changed,
        )
        self.tab_widget.addTab(self.control_panel, "Control")

        self.action_editor = ActionEditor(
            action_manager=self.action_manager,
        )
        self.tab_widget.addTab(self.action_editor, "Actions")

    def setup_menu(self):
        """Set up the menu bar."""
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")

        settings_action = QAction("Settings...", self)
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)

        file_menu.addSeparator()

        quit_action = QAction("Quit", self)
        quit_action.setShortcut("Cmd+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        help_menu = menubar.addMenu("Help")

        permissions_action = QAction("Check Permissions...", self)
        permissions_action.triggered.connect(self.show_permissions_dialog)
        help_menu.addAction(permissions_action)

    def setup_status_bar(self):
        """Set up the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.connection_indicator = QLabel()
        self.connection_indicator.setFixedWidth(12)
        self.connection_indicator.setFixedHeight(12)
        self.connection_indicator.setStyleSheet(
            "background-color: red; border-radius: 6px;"
        )

        self.connection_label = QLabel("Connection: Not Ready")

        self.macro_status_label = QLabel("Macro: Stopped")

        status_widget = QWidget()
        status_layout = QHBoxLayout(status_widget)
        status_layout.setContentsMargins(5, 0, 5, 0)
        status_layout.addWidget(self.connection_indicator)
        status_layout.addWidget(self.connection_label)
        status_layout.addStretch()
        status_layout.addWidget(self.macro_status_label)

        self.status_bar.addPermanentWidget(status_widget, 1)

    def setup_timers(self):
        """Set up periodic timers."""
        self.window_check_timer = QTimer()
        self.window_check_timer.timeout.connect(self.check_connection_status)
        self.window_check_timer.start(2000)

        self.status_update_timer = QTimer()
        self.status_update_timer.timeout.connect(self.update_macro_status)
        self.status_update_timer.start(500)

        self.check_connection_status()

    def create_input_backend(self):
        """Create an input backend based on current config."""
        if self.config.input_backend == "adb":
            return AdbInputBackend(
                adb_service=self.adb_service,
                auto_select_device=self.config.adb_auto_select_device,
                device_serial=self.config.adb_device_serial,
            )
        return DesktopInputBackend(
            click_service=self.click_service,
            window_service=self.window_service,
            focus_before_action=self.config.focus_bluestacks_before_action,
        )

    def check_connection_status(self):
        """Update connection status from the active backend."""
        status = self.input_backend.get_status()
        if status.connected:
            self.connection_indicator.setStyleSheet(
                "background-color: #4CAF50; border-radius: 6px;"
            )
            self.connection_label.setText(status.label)
            self.control_panel.set_connected(True, status.label, status.details)
        else:
            self.connection_indicator.setStyleSheet(
                "background-color: #f44336; border-radius: 6px;"
            )
            self.connection_label.setText(status.label)
            self.control_panel.set_connected(False, status.label, status.details)

    def update_macro_status(self):
        """Update the macro status display."""
        if self.macro_engine.is_running:
            if self.macro_engine.is_paused:
                self.macro_status_label.setText("Macro: Paused")
            else:
                idx = self.macro_engine.current_action_index
                total = len(self.action_manager.actions)
                self.macro_status_label.setText(f"Macro: Running ({idx + 1}/{total})")
        else:
            self.macro_status_label.setText("Macro: Stopped")

    def show_settings(self):
        """Show the settings dialog."""
        dialog = SettingsDialog(self.config, self)
        if dialog.exec():
            self.apply_runtime_config_updates()

    def on_control_panel_mode_changed(self):
        """Apply backend switch triggered from Control tab mode selector."""
        self.apply_runtime_config_updates()

    def apply_runtime_config_updates(self):
        """Re-apply runtime objects from current config values."""
        self.config.save()
        self.click_service.click_duration = self.config.click_duration
        self.input_backend = self.create_input_backend()
        self.macro_engine.set_input_backend(self.input_backend)
        self.macro_engine.config = self.config
        self.control_panel.set_input_backend(self.input_backend)
        self.control_panel.sync_from_config()
        self.check_connection_status()

    def check_permissions(self):
        """Check if permissions are granted."""
        if self.config.input_backend == "adb":
            return
        accessibility_ok = get_permission_status()

        if not accessibility_ok:
            QMessageBox.warning(
                self,
                "Permissions Required",
                "Accessibility permission is required for Desktop input mode to simulate mouse and keyboard "
                "input.\n\n"
                "Grant it in System Settings > Privacy & Security > Accessibility."
            )

    def show_permissions_dialog(self):
        """Show permissions status dialog."""
        accessibility_ok = get_permission_status()

        accessibility_status = "Granted" if accessibility_ok else "Not Granted"

        msg = QMessageBox(self)
        msg.setWindowTitle("Permission Status")
        msg.setText(f"Accessibility (Desktop mode): {accessibility_status}")

        if not accessibility_ok:
            msg.setInformativeText(
                "Click 'Open Settings' to grant Accessibility permission."
            )
            open_btn = msg.addButton(
                "Open Accessibility Settings", QMessageBox.ButtonRole.ActionRole
            )
            msg.addButton(QMessageBox.StandardButton.Close)

            msg.exec()
            if msg.clickedButton() == open_btn:
                request_accessibility()
        else:
            msg.exec()

    def closeEvent(self, event):
        """Handle window close."""
        if self.macro_engine.is_running:
            self.macro_engine.stop()

        self.config.save()
        event.accept()
