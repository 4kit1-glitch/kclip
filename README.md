# clipk

A lightweight clipboard manager built for terminal-first workflows. `clipk` captures clipboard activity, stores clips in a local SQLite database, and provides an interactive TUI for browsing, pinning, restoring, and managing saved entries.


## Overview

`clipk` is designed to keep a persistent history of clipboard content while remaining simple and focused. It works with text and file-based clipboard entries, stores metadata in a local database, and keeps the actual file payloads in a structured data directory under the user's XDG data folder.

The project is packaged as a Python application and exposes a Typer-based CLI. The main entry point is the `clipk` command, which can launch the TUI or run shortcut actions such as restoring an item or resetting the database.

---

### demo
<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/31ad010e-2b68-44d4-97e5-5b3a7d867ccc" />  

---

<img width="1325" height="395" alt="image" src="https://github.com/user-attachments/assets/a2a3532e-62ef-4b99-9510-9aa0325174cb" />

---


---
## Why this project exists

When I use programs like `yt-dlp`, I often copy links, commands, filenames, and other bits of information that I want to keep around for later. I needed a persistent clipboard so I could remember what I had clipped and restore it when I needed it again.

`clipk` is built for that workflow: a simple local clipboard history that stays available without turning into a heavy desktop app.

## Features

- Automatic clipboard capture for text and file-based content
- Persistent storage with SQLite metadata and local file handling
- Interactive terminal UI for browsing saved clips
- Pin and unpin support for important entries
- Restore clips back to the system clipboard
- XDG-compliant storage layout under `~/.local/share/kclip/`
- Compatibility with both Wayland and X11 environments
- Minimal architecture with no unnecessary background service

## Project status

This project is in an early stage of development. It works for everyday clipboard tracking, but some features are still limited or best-effort.

## Requirements

- Python 3.10 or newer
- One of the following desktop clipboard backends:
  - Wayland: `wl-clipboard` (`wl-copy`, `wl-paste`)
  - X11: `xclip`

The package dependencies are defined in `pyproject.toml` and include:

- `pyperclip`
- `pillow`
- `requests`
- `rich`

### Install the clipboard helper

```bash
# Wayland (Fedora, Ubuntu, Arch, etc.)
sudo dnf install wl-clipboard     # Fedora
sudo apt install wl-clipboard     # Debian/Ubuntu
sudo pacman -S wl-clipboard       # Arch

# X11
sudo dnf install xclip
sudo apt install xclip
```

On headless or server-style systems with no GUI session, text-only clipboard saving still works without the clipboard helper.

## Installation

From a local checkout:

```bash
git clone <repo-url>
cd my_clipboard
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

This installs the project in editable mode so the `clipk` command works against your current source tree.

## Usage

### Start the app

```bash
python -m clipk
# or
kclip
```

This opens the interactive full-scre
en table of saved clips

### Keyboard controls

| Key | Action |
| --- | --- |
| `↑` / `↓` or `w` / `s` | Move selection |
| `p` | Pin or unpin the selected clip |
| `d` | Delete the selected clip |
| `r` | Refresh from the database |
| `R` | Reset and delete everything |
| `q` | Quit |

Pinned entries are highlighted and marked with `*`.

### CLI usage

```bash
python -m clipk -h              # full help
python -m clipk -v              # print version
python -m clipk -m              # mouse support (not implemented)
python -m clipk -r              # wipe everything with confirmation
python -m clipk -n <ID>         # restore a clip by DB ID
python -m clipk list            # print saved clips as a table
python -m clipk tui             # explicit TUI launch
```

Example output for `clipk list`:

```text
  ID  TYPE    PIN  NAME
----------------------------------------
   1  text         hello world
   2  img          [IMG]/home/user/.local/share/kclip/data/images/...
   3  audio    *   [AUDIO]/home/user/.local/share/kclip/data/audios/...
```

<img width="632" height="111" alt="image" src="https://github.com/user-attachments/assets/58687c48-10e5-42ac-bd80-06dc4f89be2c" />

## How it works

`clipk` is split into a few focused modules, each with a clear responsibility.

| Module | Role |
| --- | --- |
| `clipmanager.py` | Clipboard reading and clip models |
| `filemanager.py` | File detection and storage handling |
| `storeengine.py` | SQLite metadata and persistence |
| `clipfile_link.py` | Save, delete, pin, reset, and restore flows |
| `tui.py` | Terminal UI and keyboard handling |
| `flagparser.py` | Typer CLI commands |
| `__main__.py` | Application entry point |

The data flow is simple:

```text
clipboard
   ↓
clip object
   ↓
store in SQLite and local files
   ↓
TUI reads and presents saved entries
```

The UI does not write directly to the database; it dispatches actions through the storage layer.

![kclip architecture](docs/demo-architecture.png)

## Core package layout

```text
src/
└── clipk/
    ├── __about__.py
    ├── __init__.py
    ├── __main__.py
    └── operators/
        ├── __init__.py
        ├── _bg_sync.py
        ├── clipfile_link.py
        ├── clipmanager.py
        ├── filemanager.py
        ├── flagparser.py
        ├── storeengine.py
        └── tui.py
```

## Storage layout

```text
~/.local/share/kclip/
└── data/
    ├── db/
    │   └── kclip.db
    ├── images/
    ├── audios/
    ├── videos/
    └── others/
```

The database stores metadata such as:

- unique clip identifier
- clip type
- file path or text reference
- pin state
- date and time of capture

## Database schema:

```sql
CREATE TABLE clips (
    clipID       INTEGER PRIMARY KEY AUTOINCREMENT,
    uniqueName   TEXT    NOT NULL,
    clipType     TEXT    NOT NULL,
    clipPath     TEXT,
    isPinned     INTEGER NOT NULL DEFAULT 0,
    clipData     TEXT,
    dateClipped  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Development notes

The project is intentionally modular. Most of the logic lives under `src/clipk/operators`, while the top-level package provides the CLI entry points.

Common development touchpoints include:

- `src/clipk/__main__.py` for startup
- `src/clipk/operators/tui.py` for the terminal interface
- `src/clipk/operators/storeengine.py` for persistence
- `src/clipk/operators/clipmanager.py` for clipboard integration

Background file-copy operations are handled by `_bg_sync.py`, which limits concurrency to keep the app responsive.

## Known limitations

- Wayland TUI freeze: some compositors throttle curses surfaces when the terminal loses focus, which can delay repainting even though saves continue to work.
- Media restore is best-effort: restoring an image or non-text item usually places a `file://` URI on the clipboard, which some apps accept but others do not.
- Clip type labels in the TUI can be unclear or abbreviated, making it harder to tell exactly what kind of item was saved.
- The interface is currently limited to showing only the latest 10 clips at a time, which restricts long-history browsing.
- No deduplication across sessions: the in-memory list resets when the process restarts.
- No encryption: the database and files are stored in plaintext in the XDG data directory.

## Contributing

Contributions are welcome. A good contribution generally does the following:

1. Keeps changes aligned with the existing module layout.
2. Adds or updates behavior in the correct operator module.
3. Maintains a simple API surface.
4. Keeps dependencies minimal and intentional.

## License

This project is distributed under the Apache 2.0 license. See `LICENSE` for details.

## Author

Kengah Ireneaus — [4jrkit1@gmail.com](mailto:4jrkit1@gmail.com)
