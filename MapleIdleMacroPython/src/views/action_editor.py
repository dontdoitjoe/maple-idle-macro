"""Action editor view for managing macro actions."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QDialog, QFormLayout, QLineEdit, QComboBox,
    QSpinBox, QDoubleSpinBox, QLabel, QDialogButtonBox, QGroupBox,
    QMessageBox, QFrame
)
from PyQt6.QtCore import Qt

from ..models.action import Action, ActionType, ActionManager


class ActionEditor(QWidget):
    """Widget for editing macro actions."""

    def __init__(self, action_manager: ActionManager):
        super().__init__()

        self.action_manager = action_manager

        self.setup_ui()
        self.refresh_list()

    def setup_ui(self):
        """Set up the UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)

        header = QHBoxLayout()

        title = QLabel("Macro Actions")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header.addWidget(title)

        header.addStretch()

        self.count_label = QLabel("0 actions")
        self.count_label.setStyleSheet("color: gray;")
        header.addWidget(self.count_label)

        layout.addLayout(header)

        self.action_list = QListWidget()
        self.action_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.action_list.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.action_list.itemDoubleClicked.connect(self.edit_action)
        self.action_list.model().rowsMoved.connect(self.on_rows_moved)
        layout.addWidget(self.action_list)

        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add Action")
        self.add_btn.clicked.connect(self.add_action)

        self.edit_btn = QPushButton("Edit")
        self.edit_btn.clicked.connect(self.edit_selected)

        self.remove_btn = QPushButton("Remove")
        self.remove_btn.clicked.connect(self.remove_action)

        self.move_up_btn = QPushButton("Move Up")
        self.move_up_btn.clicked.connect(self.move_up)

        self.move_down_btn = QPushButton("Move Down")
        self.move_down_btn.clicked.connect(self.move_down)

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.remove_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.move_up_btn)
        button_layout.addWidget(self.move_down_btn)

        layout.addLayout(button_layout)

        info_frame = QFrame()
        info_frame.setStyleSheet(
            "background-color: #e3f2fd; border-radius: 4px; padding: 8px;"
        )
        info_layout = QHBoxLayout(info_frame)
        info_layout.setContentsMargins(8, 8, 8, 8)

        info_label = QLabel(
            "Tip: Drag and drop actions to reorder. "
            "Double-click to edit. Key names follow PyAutoGUI in Desktop mode "
            "(e.g. space, enter, left, right, a, 1). "
            "ADB mode maps common names to Android KEYCODE values."
        )
        info_label.setStyleSheet("color: #1565c0;")
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)

        layout.addWidget(info_frame)

    def refresh_list(self):
        """Refresh the action list."""
        self.action_list.clear()

        for i, action in enumerate(self.action_manager.actions):
            item = QListWidgetItem()

            text = f"{i + 1}. {action.name}"
            if not action.enabled:
                text += " (disabled)"
            text += f"\n     {action.description}"

            item.setText(text)
            item.setData(Qt.ItemDataRole.UserRole, action.id)

            if not action.enabled:
                item.setForeground(Qt.GlobalColor.gray)

            self.action_list.addItem(item)

        self.count_label.setText(f"{len(self.action_manager.actions)} actions")

    def add_action(self):
        """Open dialog to add a new action."""
        dialog = ActionDialog(parent=self)
        if dialog.exec():
            action = dialog.get_action()
            self.action_manager.add(action)
            self.refresh_list()

    def edit_selected(self):
        """Edit the selected action."""
        current = self.action_list.currentItem()
        if current:
            self.edit_action(current)

    def edit_action(self, item: QListWidgetItem):
        """Edit an action."""
        action_id = item.data(Qt.ItemDataRole.UserRole)
        action = self.action_manager.get(action_id)

        if action:
            dialog = ActionDialog(action, parent=self)
            if dialog.exec():
                updated = dialog.get_action()
                updated.id = action.id
                self.action_manager.update(updated)
                self.refresh_list()

    def remove_action(self):
        """Remove the selected action."""
        current = self.action_list.currentItem()
        if not current:
            return

        action_id = current.data(Qt.ItemDataRole.UserRole)

        reply = QMessageBox.question(
            self,
            "Remove Action",
            "Are you sure you want to remove this action?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.action_manager.remove(action_id)
            self.refresh_list()

    def move_up(self):
        """Move selected action up."""
        current_row = self.action_list.currentRow()
        if current_row > 0:
            self.action_manager.move(current_row, current_row - 1)
            self.refresh_list()
            self.action_list.setCurrentRow(current_row - 1)

    def move_down(self):
        """Move selected action down."""
        current_row = self.action_list.currentRow()
        if current_row < len(self.action_manager.actions) - 1:
            self.action_manager.move(current_row, current_row + 1)
            self.refresh_list()
            self.action_list.setCurrentRow(current_row + 1)

    def on_rows_moved(self):
        """Handle drag-drop reordering."""
        new_order = []
        for i in range(self.action_list.count()):
            item = self.action_list.item(i)
            action_id = item.data(Qt.ItemDataRole.UserRole)
            action = self.action_manager.get(action_id)
            if action:
                new_order.append(action)

        self.action_manager.actions = new_order
        self.action_manager.save()
        self.refresh_list()


class ActionDialog(QDialog):
    """Dialog for creating/editing actions."""

    def __init__(self, action: Action = None, parent=None):
        super().__init__(parent)

        self.action = action
        self.is_edit = action is not None

        self.setup_ui()

        if self.is_edit:
            self.load_action(action)

    def setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Edit Action" if self.is_edit else "Add Action")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        form = QFormLayout()

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter action name")
        form.addRow("Name:", self.name_edit)

        self.type_combo = QComboBox()
        self.type_combo.addItem("Fixed Click", ActionType.FIXED_CLICK)
        self.type_combo.addItem("Key Press", ActionType.KEY_PRESS)
        self.type_combo.addItem("Delay", ActionType.DELAY)
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        form.addRow("Type:", self.type_combo)

        layout.addLayout(form)

        self.click_group = QGroupBox("Click Position")
        click_layout = QFormLayout(self.click_group)

        self.x_spin = QSpinBox()
        self.x_spin.setRange(0, 10000)
        click_layout.addRow("X:", self.x_spin)

        self.y_spin = QSpinBox()
        self.y_spin.setRange(0, 10000)
        click_layout.addRow("Y:", self.y_spin)

        layout.addWidget(self.click_group)

        self.key_group = QGroupBox("Key Press")
        key_layout = QFormLayout(self.key_group)

        self.key_edit = QLineEdit()
        self.key_edit.setPlaceholderText("e.g. space, enter, left, a")
        key_layout.addRow("Key name:", self.key_edit)

        self.key_hold_spin = QDoubleSpinBox()
        self.key_hold_spin.setRange(0.0, 5.0)
        self.key_hold_spin.setDecimals(3)
        self.key_hold_spin.setSingleStep(0.05)
        self.key_hold_spin.setSuffix(" seconds")
        key_layout.addRow("Hold duration:", self.key_hold_spin)

        layout.addWidget(self.key_group)

        self.delay_group = QGroupBox("Delay")
        delay_layout = QFormLayout(self.delay_group)

        self.delay_spin = QDoubleSpinBox()
        self.delay_spin.setRange(0.1, 300)
        self.delay_spin.setValue(1.0)
        self.delay_spin.setSuffix(" seconds")
        delay_layout.addRow("Duration:", self.delay_spin)

        layout.addWidget(self.delay_group)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.on_type_changed(0)

    def on_type_changed(self, index: int):
        """Handle action type change."""
        action_type = self.type_combo.currentData()

        self.click_group.setVisible(action_type == ActionType.FIXED_CLICK)
        self.key_group.setVisible(action_type == ActionType.KEY_PRESS)
        self.delay_group.setVisible(action_type == ActionType.DELAY)

        self.adjustSize()

    def load_action(self, action: Action):
        """Load action data into the form."""
        self.name_edit.setText(action.name)

        type_index = self.type_combo.findData(action.action_type)
        if type_index >= 0:
            self.type_combo.setCurrentIndex(type_index)

        self.x_spin.setValue(action.click_x)
        self.y_spin.setValue(action.click_y)
        self.key_edit.setText(action.key_name)
        self.key_hold_spin.setValue(action.key_hold_seconds)
        self.delay_spin.setValue(action.delay_seconds)

    def get_action(self) -> Action:
        """Get the action from the form."""
        action_type = self.type_combo.currentData()

        return Action(
            name=self.name_edit.text() or "Unnamed Action",
            action_type=action_type,
            click_x=self.x_spin.value(),
            click_y=self.y_spin.value(),
            delay_seconds=self.delay_spin.value(),
            key_name=self.key_edit.text().strip(),
            key_hold_seconds=self.key_hold_spin.value(),
        )
