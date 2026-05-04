"""Action model for macro steps."""

import json
import uuid
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field


class ActionType(Enum):
    """Types of macro actions."""
    FIXED_CLICK = "fixed_click"
    DELAY = "delay"
    KEY_PRESS = "key_press"


@dataclass
class Action:
    """A single macro action."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    action_type: ActionType = ActionType.FIXED_CLICK
    enabled: bool = True

    click_x: int = 0
    click_y: int = 0

    delay_seconds: float = 1.0

    key_name: str = ""
    key_hold_seconds: float = 0.0

    @property
    def description(self) -> str:
        """Get a human-readable description of the action."""
        if self.action_type == ActionType.FIXED_CLICK:
            return f"Click at ({self.click_x}, {self.click_y})"
        elif self.action_type == ActionType.DELAY:
            return f"Delay {self.delay_seconds}s"
        elif self.action_type == ActionType.KEY_PRESS:
            hold = f", hold {self.key_hold_seconds}s" if self.key_hold_seconds > 0 else ""
            return f"Key: {self.key_name or '(none)'}{hold}"
        return "Unknown action"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'action_type': self.action_type.value,
            'enabled': self.enabled,
            'click_x': self.click_x,
            'click_y': self.click_y,
            'delay_seconds': self.delay_seconds,
            'key_name': self.key_name,
            'key_hold_seconds': self.key_hold_seconds,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Action':
        """Create an Action from a dictionary."""
        action_type_str = data.get('action_type', 'fixed_click')
        if action_type_str == 'template_click':
            return cls(
                id=data.get('id', str(uuid.uuid4())),
                name=f"[removed template] {data.get('name', '')}".strip(),
                action_type=ActionType.DELAY,
                enabled=False,
                delay_seconds=0.1,
                key_name='',
                key_hold_seconds=0.0,
            )
        try:
            action_type = ActionType(action_type_str)
        except ValueError:
            action_type = ActionType.FIXED_CLICK

        return cls(
            id=data.get('id', str(uuid.uuid4())),
            name=data.get('name', ''),
            action_type=action_type,
            enabled=data.get('enabled', True),
            click_x=data.get('click_x', 0),
            click_y=data.get('click_y', 0),
            delay_seconds=data.get('delay_seconds', 1.0),
            key_name=data.get('key_name', ''),
            key_hold_seconds=float(data.get('key_hold_seconds', 0.0)),
        )

    @classmethod
    def fixed_click(cls, name: str, x: int, y: int) -> 'Action':
        """Create a fixed click action."""
        return cls(
            name=name,
            action_type=ActionType.FIXED_CLICK,
            click_x=x,
            click_y=y
        )

    @classmethod
    def delay(cls, name: str, seconds: float) -> 'Action':
        """Create a delay action."""
        return cls(
            name=name,
            action_type=ActionType.DELAY,
            delay_seconds=seconds
        )

    @classmethod
    def key_press(cls, name: str, key_name: str, hold_seconds: float = 0.0) -> 'Action':
        """Create a key press action."""
        return cls(
            name=name,
            action_type=ActionType.KEY_PRESS,
            key_name=key_name,
            key_hold_seconds=hold_seconds,
        )


class ActionManager:
    """Manager for loading and saving actions."""

    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.actions: List[Action] = []
        self.load()

    def load(self):
        """Load actions from disk."""
        if not self.storage_path.exists():
            self.actions = []
            return

        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
            migrated = any(
                isinstance(a, dict) and a.get('action_type') == 'template_click'
                for a in data
            )
            self.actions = [Action.from_dict(a) for a in data]
            if migrated:
                self.save()
        except (json.JSONDecodeError, IOError):
            self.actions = []

    def save(self):
        """Save actions to disk."""
        data = [a.to_dict() for a in self.actions]
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)

    def add(self, action: Action):
        """Add an action."""
        self.actions.append(action)
        self.save()

    def remove(self, action_id: str):
        """Remove an action by ID."""
        self.actions = [a for a in self.actions if a.id != action_id]
        self.save()

    def get(self, action_id: str) -> Optional[Action]:
        """Get an action by ID."""
        for a in self.actions:
            if a.id == action_id:
                return a
        return None

    def update(self, action: Action):
        """Update an existing action."""
        for i, a in enumerate(self.actions):
            if a.id == action.id:
                self.actions[i] = action
                self.save()
                return

    def move(self, from_index: int, to_index: int):
        """Move an action from one position to another."""
        if 0 <= from_index < len(self.actions) and 0 <= to_index < len(self.actions):
            action = self.actions.pop(from_index)
            self.actions.insert(to_index, action)
            self.save()

    def clear(self):
        """Clear all actions."""
        self.actions = []
        self.save()
