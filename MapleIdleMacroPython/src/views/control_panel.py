"""Control panel view for macro controls."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QLabel, QCheckBox, QComboBox, QDoubleSpinBox,
    QProgressBar, QFrame, QScrollArea
)
from PyQt6.QtCore import QTimer

from ..models.action import ActionType


class ControlPanel(QWidget):
    """Control panel for starting/stopping macros."""

    def __init__(
        self,
        macro_engine,
        window_service,
        click_service,
        input_backend,
        config,
        refresh_status_callback=None,
        mode_change_callback=None,
    ):
        super().__init__()

        self.macro_engine = macro_engine
        self.window_service = window_service
        self.click_service = click_service
        self.input_backend = input_backend
        self.config = config
        self.refresh_status_callback = refresh_status_callback
        self.mode_change_callback = mode_change_callback

        self.is_connected = False

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """Set up the UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(16)

        status_group = QGroupBox("Connection Status")
        status_layout = QVBoxLayout(status_group)

        status_row = QHBoxLayout()
        self.status_icon = QLabel()
        self.status_icon.setFixedSize(16, 16)
        self.status_icon.setStyleSheet(
            "background-color: #f44336; border-radius: 8px;"
        )
        self.status_label = QLabel("BlueStacks Not Found")
        self.status_label.setStyleSheet("font-weight: bold;")
        status_row.addWidget(self.status_icon)
        status_row.addWidget(self.status_label)
        status_row.addStretch()

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setFixedWidth(80)
        status_row.addWidget(self.refresh_btn)

        status_layout.addLayout(status_row)

        self.window_info_label = QLabel("Window: --")
        self.window_info_label.setStyleSheet("color: gray;")
        status_layout.addWidget(self.window_info_label)

        scroll_layout.addWidget(status_group)

        control_group = QGroupBox("Macro Controls")
        control_layout = QVBoxLayout(control_group)

        button_row = QHBoxLayout()

        self.start_btn = QPushButton("Start")
        self.start_btn.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; "
            "padding: 12px 24px; font-size: 14px; font-weight: bold; }"
            "QPushButton:disabled { background-color: #ccc; }"
        )
        self.start_btn.setEnabled(False)

        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setStyleSheet(
            "QPushButton { background-color: #FF9800; color: white; "
            "padding: 12px 24px; font-size: 14px; font-weight: bold; }"
            "QPushButton:disabled { background-color: #ccc; }"
        )
        self.pause_btn.setEnabled(False)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setStyleSheet(
            "QPushButton { background-color: #f44336; color: white; "
            "padding: 12px 24px; font-size: 14px; font-weight: bold; }"
            "QPushButton:disabled { background-color: #ccc; }"
        )
        self.stop_btn.setEnabled(False)

        button_row.addWidget(self.start_btn)
        button_row.addWidget(self.pause_btn)
        button_row.addWidget(self.stop_btn)

        control_layout.addLayout(button_row)

        progress_layout = QVBoxLayout()

        progress_label_row = QHBoxLayout()
        self.progress_label = QLabel("Progress:")
        self.progress_info = QLabel("0 / 0")
        progress_label_row.addWidget(self.progress_label)
        progress_label_row.addStretch()
        progress_label_row.addWidget(self.progress_info)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)

        progress_layout.addLayout(progress_label_row)
        progress_layout.addWidget(self.progress_bar)

        control_layout.addLayout(progress_layout)

        self.current_action_label = QLabel("Current: --")
        self.current_action_label.setStyleSheet("font-style: italic; color: gray;")
        control_layout.addWidget(self.current_action_label)

        scroll_layout.addWidget(control_group)

        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(options_group)

        self.loop_checkbox = QCheckBox("Loop macro continuously")
        self.loop_checkbox.setChecked(self.config.loop_enabled)
        options_layout.addWidget(self.loop_checkbox)

        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("Input mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Focus mode (Desktop)", "desktop")
        self.mode_combo.addItem("ADB mode (Background)", "adb")
        mode_idx = self.mode_combo.findData(self.config.input_backend)
        if mode_idx >= 0:
            self.mode_combo.setCurrentIndex(mode_idx)
        mode_row.addWidget(self.mode_combo)
        mode_row.addStretch()
        options_layout.addLayout(mode_row)

        self.focus_checkbox = QCheckBox(
            "Focus BlueStacks before each click / key action"
        )
        self.focus_checkbox.setChecked(self.config.focus_bluestacks_before_action)
        options_layout.addWidget(self.focus_checkbox)

        delay_row = QHBoxLayout()
        delay_row.addWidget(QLabel("Delay between actions:"))
        self.delay_spinbox = QDoubleSpinBox()
        self.delay_spinbox.setRange(0.1, 60.0)
        self.delay_spinbox.setValue(self.config.default_delay)
        self.delay_spinbox.setSuffix(" sec")
        self.delay_spinbox.setSingleStep(0.1)
        delay_row.addWidget(self.delay_spinbox)
        delay_row.addStretch()
        options_layout.addLayout(delay_row)

        scroll_layout.addWidget(options_group)

        quick_group = QGroupBox("Quick Actions")
        quick_layout = QHBoxLayout(quick_group)

        self.test_click_btn = QPushButton("Test Click (Center)")
        self.test_click_btn.setEnabled(False)

        quick_layout.addWidget(self.test_click_btn)

        scroll_layout.addWidget(quick_group)

        scroll_layout.addStretch()

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_progress)
        self.update_timer.start(200)

    def setup_connections(self):
        """Set up signal connections."""
        self.refresh_btn.clicked.connect(self.refresh_connection)
        self.start_btn.clicked.connect(self.start_macro)
        self.pause_btn.clicked.connect(self.toggle_pause)
        self.stop_btn.clicked.connect(self.stop_macro)
        self.test_click_btn.clicked.connect(self.test_click)
        self.loop_checkbox.toggled.connect(self.on_loop_changed)
        self.delay_spinbox.valueChanged.connect(self.on_delay_changed)
        self.focus_checkbox.toggled.connect(self.on_focus_changed)
        self.mode_combo.currentIndexChanged.connect(self.on_mode_changed)

    def on_focus_changed(self, checked: bool):
        self.config.focus_bluestacks_before_action = checked
        self.config.save()

    def on_mode_changed(self, _index: int):
        selected = self.mode_combo.currentData()
        if selected not in ("desktop", "adb"):
            return
        if selected == self.config.input_backend:
            return
        self.config.input_backend = selected
        self.config.save()
        if self.mode_change_callback:
            self.mode_change_callback()

    def set_input_backend(self, input_backend):
        self.input_backend = input_backend
        idx = self.mode_combo.findData(self.config.input_backend)
        if idx >= 0 and idx != self.mode_combo.currentIndex():
            self.mode_combo.blockSignals(True)
            self.mode_combo.setCurrentIndex(idx)
            self.mode_combo.blockSignals(False)
        self.update_focus_control_state()
        self.update_button_states()

    def set_connected(self, connected: bool, status_label: str, details: str = ""):
        """Update connection status."""
        self.is_connected = connected

        if connected:
            self.status_icon.setStyleSheet(
                "background-color: #4CAF50; border-radius: 8px;"
            )
            self.status_label.setText(status_label)
            self.window_info_label.setText(details or "Connected")
        else:
            self.status_icon.setStyleSheet(
                "background-color: #f44336; border-radius: 8px;"
            )
            self.status_label.setText(status_label)
            self.window_info_label.setText(details or "Not connected")

        self.update_button_states()

    def update_button_states(self):
        """Update button enabled states."""
        running = self.macro_engine.is_running
        paused = self.macro_engine.is_paused
        actions = self.macro_engine.action_manager.actions
        has_actions = len(actions) > 0
        needs_connection = any(
            a.enabled and a.action_type != ActionType.DELAY for a in actions
        )
        if self.input_backend.backend_id == "desktop":
            needs_connection = any(
                a.enabled and a.action_type == ActionType.FIXED_CLICK for a in actions
            )
        can_start = has_actions and (not needs_connection or self.is_connected)

        self.start_btn.setEnabled(can_start and not running)
        self.pause_btn.setEnabled(running)
        self.stop_btn.setEnabled(running)

        self.pause_btn.setText("Resume" if paused else "Pause")

        self.test_click_btn.setEnabled(
            self.is_connected and self.input_backend.backend_id == "desktop"
        )
        self.update_focus_control_state()

    def update_focus_control_state(self):
        desktop_mode = self.input_backend.backend_id == "desktop"
        self.focus_checkbox.setEnabled(desktop_mode)
        if desktop_mode:
            self.focus_checkbox.setToolTip("")
        else:
            self.focus_checkbox.setToolTip(
                "Focus option only applies to desktop input mode."
            )

    def update_progress(self):
        """Update progress display."""
        if self.macro_engine.is_running:
            total = len(self.macro_engine.action_manager.actions)
            current = self.macro_engine.current_action_index

            if total > 0:
                progress = int((current / total) * 100)
                self.progress_bar.setValue(progress)
                self.progress_info.setText(f"{current + 1} / {total}")

                if current < total:
                    action = self.macro_engine.action_manager.actions[current]
                    self.current_action_label.setText(f"Current: {action.name}")
            else:
                self.progress_bar.setValue(0)
                self.progress_info.setText("0 / 0")
                self.current_action_label.setText("Current: --")
        else:
            self.progress_bar.setValue(0)
            total = len(self.macro_engine.action_manager.actions)
            self.progress_info.setText(f"0 / {total}")
            self.current_action_label.setText("Current: --")

        self.update_button_states()

    def refresh_connection(self):
        """Refresh the BlueStacks connection."""
        if self.refresh_status_callback:
            self.refresh_status_callback()

    def start_macro(self):
        """Start the macro."""
        self.macro_engine.loop_enabled = self.loop_checkbox.isChecked()
        self.macro_engine.action_delay = self.delay_spinbox.value()
        self.macro_engine.start()
        self.update_button_states()

    def toggle_pause(self):
        """Toggle pause state."""
        if self.macro_engine.is_paused:
            self.macro_engine.resume()
        else:
            self.macro_engine.pause()
        self.update_button_states()

    def stop_macro(self):
        """Stop the macro."""
        self.macro_engine.stop()
        self.update_button_states()

    def test_click(self):
        """Test click at the center of the window."""
        if self.input_backend.backend_id != "desktop":
            return
        window = self.window_service.current_window
        if not window:
            return

        center_x = int(window.width / 2)
        center_y = int(window.height / 2)

        self.click_service.click(center_x, center_y, window.bounds)

    def on_loop_changed(self, checked: bool):
        """Handle loop checkbox change."""
        self.macro_engine.loop_enabled = checked

    def on_delay_changed(self, value: float):
        """Handle delay spinbox change."""
        self.macro_engine.action_delay = value

    def sync_from_config(self):
        """Reload option widgets from config (e.g. after Settings dialog)."""
        self.loop_checkbox.setChecked(self.config.loop_enabled)
        mode_idx = self.mode_combo.findData(self.config.input_backend)
        if mode_idx >= 0:
            self.mode_combo.blockSignals(True)
            self.mode_combo.setCurrentIndex(mode_idx)
            self.mode_combo.blockSignals(False)
        self.delay_spinbox.blockSignals(True)
        self.delay_spinbox.setValue(self.config.default_delay)
        self.delay_spinbox.blockSignals(False)
        self.focus_checkbox.blockSignals(True)
        self.focus_checkbox.setChecked(self.config.focus_bluestacks_before_action)
        self.focus_checkbox.blockSignals(False)
        self.update_focus_control_state()
        self.macro_engine.loop_enabled = self.config.loop_enabled
        self.macro_engine.action_delay = self.config.default_delay
