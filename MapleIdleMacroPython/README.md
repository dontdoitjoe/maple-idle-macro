# Maple Idle Macro - Python Edition

A Python-based macOS automation tool for Maple Idle running on BlueStacks Air emulator.

## Features

- **Dual Input Backends**: Choose Desktop (PyAutoGUI) or ADB (Android Debug Bridge)
- **Background Input via ADB**: Send taps and key events without focusing BlueStacks
- **Desktop Automation**: Clicks/keys through macOS Accessibility when using Desktop mode
- **Macro Sequencing**: Create sequences of actions with configurable delay between steps
- **Loop Support**: Run macros continuously or once

## Requirements

- macOS 13.0 (Ventura) or later
- Python 3.10 or later (3.11–3.12 recommended for PyInstaller builds)
- BlueStacks Air emulator
- Android Platform Tools (`adb`) if you use ADB mode

## Installation

### Option 1: Run from Source

1. Clone or download this project

2. Create a virtual environment:
   ```bash
   cd MapleIdleMacroPython
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the app:
   ```bash
   python main.py
   ```

### Option 2: Build Standalone App (for sharing)

From the project folder, with a venv that has `requirements.txt` installed:

```bash
./build_mac_app.sh
```

This installs PyInstaller if needed, runs `pyinstaller build.spec`, and produces:

- **`dist/MapleIdleMacro.app`** — drag this to **Applications** (or open it from Finder like any app).
- **`release/MapleIdleMacro-macos.zip`** — share this zip; recipients unzip, then drag **`MapleIdleMacro.app`** to Applications.

Recipients **do not** need Python or Terminal. They may need to allow the app in **System Settings > Privacy & Security** if macOS blocks an unsigned download (see Troubleshooting).

To build manually:

```bash
pip install pyinstaller
pyinstaller build.spec
```

The app will be in `dist/MapleIdleMacro.app`.

If the built app does nothing when double-clicked, build once with a console to see errors:

```bash
pyinstaller --onefile --windowed --name MapleIdleMacroDebug main.py
# Or temporarily set console=True in build.spec on the EXE() line, rebuild, run from dist/
```

## Permissions and dependencies

- **Desktop mode**:
  - Requires **Accessibility** permission for synthetic input.
  - Optional **Automation** prompt may appear if AppleScript focus fallback is used.
- **ADB mode**:
  - Does not require BlueStacks window focus.
  - Requires `adb` installed and a connected/authorized Android device endpoint.
  - The packaged app checks common macOS install locations like `/opt/homebrew/bin/adb` and `/usr/local/bin/adb`.

Screen Recording is **not** required in either mode.

## Usage

### Getting Started

1. Launch BlueStacks Air and open Maple Idle
2. Run the Maple Idle Macro app
3. Choose backend in **File > Settings**:
   - **Desktop (PyAutoGUI)** for foreground desktop automation
   - **ADB** for background emulator input
4. Grant Accessibility only if using Desktop mode

### Creating Actions

1. Go to the **Actions** tab
2. Click **Add Action**
3. Choose the action type:
   - **Fixed Click**: Click at specific X,Y coordinates (relative to the BlueStacks window)
   - **Key Press**: Send a key; set an optional **hold** duration (seconds)
   - **Delay**: Wait for a specified time
4. Key names:
   - Desktop mode: [PyAutoGUI keyboard keys](https://pyautogui.readthedocs.io/en/latest/keyboard.html#keyboard-keys)
   - ADB mode: common names map to Android keycodes (`space`, `enter`, arrows, single letters/digits), or provide `KEYCODE_*`

**Timing:** Use **Delay between actions** on the Control tab (and Delay actions) for spacing between steps. Use **Hold duration** on a Key Press action to hold a key down before release.

### Running the Macro

1. Go to the **Control** tab
2. Configure options (loop, delay between actions, backend-specific settings)
3. Click **Start**; use **Pause** / **Stop** as needed

### Settings

Use **File > Settings** for defaults (loop, delays, click duration, backend mode, and ADB target selection).

## Project Structure

```
MapleIdleMacroPython/
├── main.py                    # Entry point (logs startup failures to Application Support)
├── requirements.txt           # Python dependencies
├── build.spec                 # PyInstaller config
├── src/
│   ├── app.py                 # Main application window
│   ├── macro_engine.py        # Macro execution engine
│   ├── services/
│   │   ├── window_service.py      # BlueStacks detection and activation (desktop mode)
│   │   ├── click_service.py       # Mouse and keyboard simulation (desktop mode)
│   │   ├── adb_service.py         # ADB command execution and key/tap mapping
│   │   └── input_backend.py       # Desktop/ADB backend abstraction
│   ├── models/
│   │   └── action.py              # Macro action model
│   ├── views/
│   │   ├── control_panel.py       # Start/stop controls
│   │   ├── action_editor.py       # Action list management
│   │   └── settings_dialog.py     # Settings
│   └── utils/
│       ├── config.py              # Settings persistence
│       └── permissions.py         # macOS permission checks
└── resources/
```

## Troubleshooting

### Desktop mode: BlueStacks not detected

- Make sure BlueStacks Air is running (not only in the dock without a window)
- Click **Refresh** in the Control panel

### Desktop mode: clicks or keys not working

- Grant **Accessibility** in System Settings
- Enable **Focus BlueStacks before each click / key action** so the emulator receives input
- If focus still fails, approve any **Automation** prompt for AppleScript

### ADB mode: not connected / no input

- Confirm `adb` is installed:
  ```bash
  adb version
  ```
- Check device visibility:
  ```bash
  adb devices
  ```
- If device shows `unauthorized`, approve authorization in BlueStacks.
- In app settings, enable **auto-select first online device** or set a serial override (for example `127.0.0.1:5555`).

### App does not open (standalone .app)

- Check `~/Library/Application Support/MapleIdleMacro/launch.log` for a traceback
- Run from Terminal to see errors: `python3 main.py` (from the project folder with venv activated)
- If macOS blocked the download, clear quarantine (adjust the path to your copy of the app):

  ```bash
  xattr -dr com.apple.quarantine "/path/to/MapleIdleMacro.app"
  ```

- Use Python **3.11 or 3.12** for building if you hit compatibility issues with newer Python versions

### Older macros that used “Template click”

Those steps are migrated to a short, **disabled** delay named `[removed template] …` so they do not click at (0,0). Edit or remove them in the Actions tab.

## License

This project is for personal use only.
