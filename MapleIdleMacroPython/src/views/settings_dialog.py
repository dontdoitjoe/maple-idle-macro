"""Settings dialog for application configuration."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QCheckBox, QComboBox, QDoubleSpinBox, QLineEdit, QLabel, QPushButton,
    QDialogButtonBox, QTabWidget, QWidget
)

from ..utils.config import Config
from ..utils.permissions import get_permission_status, request_accessibility


class SettingsDialog(QDialog):
    """Settings dialog."""

    def __init__(self, config: Config, parent=None):
        super().__init__(parent)

        self.config = config
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Settings")
        self.setMinimumWidth(450)

        layout = QVBoxLayout(self)

        tabs = QTabWidget()
        layout.addWidget(tabs)

        macro_tab = QWidget()
        macro_layout = QVBoxLayout(macro_tab)

        behavior_group = QGroupBox("Behavior")
        behavior_layout = QFormLayout(behavior_group)

        self.loop_checkbox = QCheckBox("Loop macro continuously")
        behavior_layout.addRow(self.loop_checkbox)

        self.delay_spin = QDoubleSpinBox()
        self.delay_spin.setRange(0.1, 60.0)
        self.delay_spin.setSuffix(" seconds")
        self.delay_spin.setSingleStep(0.1)
        behavior_layout.addRow("Default delay:", self.delay_spin)

        self.focus_checkbox = QCheckBox(
            "Focus BlueStacks before each click / key action"
        )
        behavior_layout.addRow(self.focus_checkbox)

        self.backend_combo = QComboBox()
        self.backend_combo.addItem("Desktop (PyAutoGUI)", "desktop")
        self.backend_combo.addItem("ADB (Background input)", "adb")
        self.backend_combo.currentIndexChanged.connect(self.on_backend_changed)
        behavior_layout.addRow("Input backend:", self.backend_combo)

        self.adb_auto_checkbox = QCheckBox("Auto-select first online ADB device")
        behavior_layout.addRow(self.adb_auto_checkbox)

        self.adb_serial_edit = QLineEdit()
        self.adb_serial_edit.setPlaceholderText("Optional override, e.g. 127.0.0.1:5555")
        behavior_layout.addRow("ADB device serial:", self.adb_serial_edit)

        macro_layout.addWidget(behavior_group)

        click_group = QGroupBox("Click Settings")
        click_layout = QFormLayout(click_group)

        self.click_duration_spin = QDoubleSpinBox()
        self.click_duration_spin.setRange(0.01, 1.0)
        self.click_duration_spin.setSuffix(" seconds")
        self.click_duration_spin.setSingleStep(0.01)
        self.click_duration_spin.setDecimals(3)
        click_layout.addRow("Click duration:", self.click_duration_spin)

        macro_layout.addWidget(click_group)
        macro_layout.addStretch()

        tabs.addTab(macro_tab, "Macro")

        permissions_tab = QWidget()
        permissions_layout = QVBoxLayout(permissions_tab)

        permissions_group = QGroupBox("Required Permissions")
        perm_layout = QVBoxLayout(permissions_group)

        accessibility_row = QHBoxLayout()
        self.accessibility_status = QLabel()
        self.accessibility_status.setFixedWidth(20)
        accessibility_row.addWidget(self.accessibility_status)
        accessibility_row.addWidget(QLabel("Accessibility"))
        accessibility_row.addStretch()
        self.accessibility_btn = QPushButton("Grant")
        self.accessibility_btn.setFixedWidth(80)
        self.accessibility_btn.clicked.connect(request_accessibility)
        accessibility_row.addWidget(self.accessibility_btn)
        perm_layout.addLayout(accessibility_row)

        accessibility_help = QLabel(
            "Required for Desktop input mode to simulate mouse clicks and keyboard keys."
        )
        accessibility_help.setStyleSheet("color: gray; font-size: 11px; margin-left: 24px;")
        perm_layout.addWidget(accessibility_help)

        automation_help = QLabel(
            "If BlueStacks does not come to the front, the app may use AppleScript "
            "as a fallback; macOS may then ask for Automation permission for "
            "System Events / BlueStacks."
        )
        automation_help.setWordWrap(True)
        automation_help.setStyleSheet("color: gray; font-size: 11px; margin-left: 24px;")
        perm_layout.addWidget(automation_help)

        permissions_layout.addWidget(permissions_group)

        refresh_btn = QPushButton("Refresh Permission Status")
        refresh_btn.clicked.connect(self.update_permission_status)
        permissions_layout.addWidget(refresh_btn)

        permissions_layout.addStretch()

        tabs.addTab(permissions_tab, "Permissions")

        about_tab = QWidget()
        about_layout = QVBoxLayout(about_tab)

        about_group = QGroupBox("About")
        about_inner = QVBoxLayout(about_group)

        title = QLabel("Maple Idle Macro")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        about_inner.addWidget(title)

        version = QLabel("Version 1.0 (Python Edition)")
        version.setStyleSheet("color: gray;")
        about_inner.addWidget(version)

        about_inner.addSpacing(16)

        desc = QLabel(
            "A macOS automation tool for Maple Idle running on BlueStacks Air.\n\n"
            "Built with PyQt6 and pyautogui."
        )
        desc.setWordWrap(True)
        about_inner.addWidget(desc)

        about_layout.addWidget(about_group)
        about_layout.addStretch()

        tabs.addTab(about_tab, "About")

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Apply
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.apply_settings)
        layout.addWidget(buttons)

        self.update_permission_status()

    def load_settings(self):
        """Load current settings into the form."""
        self.loop_checkbox.setChecked(self.config.loop_enabled)
        self.delay_spin.setValue(self.config.default_delay)
        self.click_duration_spin.setValue(self.config.click_duration)
        self.focus_checkbox.setChecked(self.config.focus_bluestacks_before_action)
        backend_idx = self.backend_combo.findData(self.config.input_backend)
        if backend_idx >= 0:
            self.backend_combo.setCurrentIndex(backend_idx)
        self.adb_auto_checkbox.setChecked(self.config.adb_auto_select_device)
        self.adb_serial_edit.setText(self.config.adb_device_serial)
        self.on_backend_changed(self.backend_combo.currentIndex())

    def apply_settings(self):
        """Apply settings without closing."""
        self.config.loop_enabled = self.loop_checkbox.isChecked()
        self.config.default_delay = self.delay_spin.value()
        self.config.click_duration = self.click_duration_spin.value()
        self.config.focus_bluestacks_before_action = self.focus_checkbox.isChecked()
        self.config.input_backend = self.backend_combo.currentData()
        self.config.adb_auto_select_device = self.adb_auto_checkbox.isChecked()
        self.config.adb_device_serial = self.adb_serial_edit.text().strip()
        self.config.save()

    def on_backend_changed(self, _index: int):
        backend = self.backend_combo.currentData()
        is_adb = backend == "adb"
        self.focus_checkbox.setEnabled(not is_adb)
        self.adb_auto_checkbox.setEnabled(is_adb)
        self.adb_serial_edit.setEnabled(is_adb)

    def accept(self):
        """Apply settings and close."""
        self.apply_settings()
        super().accept()

    def update_permission_status(self):
        """Update the permission status display."""
        accessibility_ok = get_permission_status()

        if accessibility_ok:
            self.accessibility_status.setText("✓")
            self.accessibility_status.setStyleSheet("color: #4CAF50; font-weight: bold;")
            self.accessibility_btn.setEnabled(False)
            self.accessibility_btn.setText("Granted")
        else:
            self.accessibility_status.setText("✗")
            self.accessibility_status.setStyleSheet("color: #f44336; font-weight: bold;")
            self.accessibility_btn.setEnabled(True)
            self.accessibility_btn.setText("Grant")
