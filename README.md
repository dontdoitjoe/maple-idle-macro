# Maple Idle Macro

macOS automation for **Maple Idle** on **BlueStacks Air**: macro sequences with **desktop (PyAutoGUI)** or **ADB** input.

## Download (macOS)

Prebuilt apps are attached to **[GitHub Releases](https://github.com/dontdoitjoe/maple-idle-macro/releases)** (look for `MapleIdleMacro-macos.zip`).

1. Download the zip from the latest release.
2. Unzip, drag **`MapleIdleMacro.app`** into **Applications**.
3. Open from **Finder** the first time. If macOS blocks an unsigned app: **System Settings → Privacy & Security → Open Anyway**, or run:

   ```bash
   xattr -dr com.apple.quarantine "/path/to/MapleIdleMacro.app"
   ```

## Documentation and source

Full feature list, requirements, ADB setup, usage, troubleshooting, and **run from source** / **local build** instructions: **[`MapleIdleMacroPython/README.md`](MapleIdleMacroPython/README.md)**.

Quick local build of a shareable `.app` and zip (from `MapleIdleMacroPython/` with a venv):

```bash
./build_mac_app.sh
```

Output: `dist/MapleIdleMacro.app` and `release/MapleIdleMacro-macos.zip`.

## Publishing a new release (maintainers)

After `./build_mac_app.sh`, upload **`MapleIdleMacroPython/release/MapleIdleMacro-macos.zip`** as a release asset (large zips are not committed to git due to GitHub file-size limits):

1. **[Draft a new release](https://github.com/dontdoitjoe/maple-idle-macro/releases/new)**.
2. Tag (e.g. `v1.0.0`) and title.
3. Attach `MapleIdleMacro-macos.zip`, then publish.

With [GitHub CLI](https://cli.github.com/): `brew install gh`, `gh auth login`, then `gh release create` with `--attach` for the zip.

## License

See [`MapleIdleMacroPython/README.md`](MapleIdleMacroPython/README.md).
