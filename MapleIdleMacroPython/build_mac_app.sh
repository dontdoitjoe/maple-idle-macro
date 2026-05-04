#!/usr/bin/env bash
# Build a double-clickable MapleIdleMacro.app and a zip you can share.
# Usage: ./build_mac_app.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

VENV_PY="${ROOT}/venv/bin/python"
if [[ ! -x "$VENV_PY" ]]; then
  echo "No venv found. Create one and install deps:"
  echo "  cd \"$ROOT\""
  echo "  python3 -m venv venv"
  echo "  source venv/bin/activate"
  echo "  pip install -r requirements.txt pyinstaller"
  exit 1
fi

echo "Installing dependencies and PyInstaller..."
"$VENV_PY" -m pip install -q -r requirements.txt pyinstaller

echo "Running PyInstaller (this may take a minute)..."
"$VENV_PY" -m PyInstaller build.spec --noconfirm

APP="${ROOT}/dist/MapleIdleMacro.app"
if [[ ! -d "$APP" ]]; then
  echo "Build failed: $APP not found."
  exit 1
fi

mkdir -p "${ROOT}/release"
ZIP="${ROOT}/release/MapleIdleMacro-macos.zip"
rm -f "$ZIP"
( cd "${ROOT}/dist" && zip -rq "$ZIP" MapleIdleMacro.app )
STAMP="$(date +%Y%m%d)"
cp -f "$ZIP" "${ROOT}/release/MapleIdleMacro-macos-${STAMP}.zip"

echo ""
echo "Done."
echo "  Application: $APP"
echo "  Share this zip: $ZIP"
echo "  (dated copy: ${ROOT}/release/MapleIdleMacro-macos-${STAMP}.zip)"
echo ""
echo "Recipients can drag MapleIdleMacro.app to Applications and open it from Finder."
echo "If macOS blocks the app (unsigned), they may need: System Settings > Privacy &"
echo "Security > Open Anyway, or: xattr -dr com.apple.quarantine /path/to/MapleIdleMacro.app"
