"""
Storage engine module for kclip
contains functions to:
    - manipulate database
    - create nessesary dirs
    - add remove modify a clip
    - open and close connections
    - initialize connection

"""

import os
import sys
import atexit
import sqlite3
from pathlib import Path
from clipmanager import Clip, TextClip, AudioClip, ImageClip, VideoClip, OtherClip


APP_NAME = "kclip"
DATABASE_NAME = "kclip.db"

_conn = None
_initialized = False


def get_data_dir() -> Path:
    """returns linux standard data dir"""
    xdg_data_home = os.environ.get("XDG_DATA_HOME")
    if xdg_data_home:
        data_dir = Path(xdg_data_home) / APP_NAME / "data"
    else:
        data_dir = Path.home() / ".local" / "share" / APP_NAME / "data"
    return data_dir


def get_db_dir() -> Path:
    """returns the path of database"""
    return get_data_dir() / "db"


def get_db_path() -> Path:
    return get_db_dir() / DATABASE_NAME


def close_db() -> None:
    global _conn
    if _conn is not None:
        _conn.close()
        _conn = None


def get_connection():
    global _conn

    if _conn is None:
        _conn = sqlite3.connect(get_db_path())
        _conn.execute(
            "PRAGMA journal_mode=WAL"
        )  # this ensures the database doesnt crash on simultanuous reads
        _conn.row_factory = sqlite3.Row
        atexit.register(close_db)

    return _conn


def create_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def create_db() -> None:
    """creates the kclip database"""

    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS clips (
            clipID INTEGER PRIMARY KEY AUTOINCREMENT,
            uniqueName TEXT NOT NULL DEFAULT "text",
            clipType TEXT NOT NULL,
            clipPath TEXT,
            isPinned INTEGER NOT NULL DEFAULT 0,
            clipData TEXT,
            dateClipped TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
    """)


def delete_db() -> None:
    """deletes kclip database"""
    db_path = get_db_path()
    try:
        close_db()
    except sqlite3.Error:
        print("[error] failed to close database", file=sys.stderr)
    finally:
        db_path.unlink(missing_ok=True)
        db_path.with_suffix(".db-wal").unlink(missing_ok=True)
        db_path.with_suffix(".db-shm").unlink(missing_ok=True)



def add_record(
    unique_name: str,
    clip_type: str,
    is_pinned: bool,
    clip_path: Path | str | None = None,
    clip_data: str | None = None
) -> None:
    """adds a record to database"""
    pinstatus = 1 if is_pinned else 0
    path_value = str(clip_path) if clip_path is not None else None

    conn = get_connection()

    conn.execute(
        "INSERT INTO clips (uniqueName, clipType, clipPath, isPinned, clipData) VALUES (?, ?, ?, ?, ?)",
        (unique_name, clip_type, path_value, pinstatus, clip_data),
    )
    conn.commit()


def read_record(
    clip_id: int | None = None, unique_name: str | None = None
) -> dict | None:
    """reads a specific record from database provided with either the clip_id or
    unique_name
    """
    conn = get_connection()
    if clip_id is not None:
        result = conn.execute(" SELECT * FROM clips WHERE clipID = ?", (clip_id,))
    elif unique_name is not None:
        result = conn.execute(
            " SELECT * FROM clips WHERE uniqueName = ?", (unique_name,)
        )
    else:
        return None

    record = result.fetchone()

    if record is None:
        return None

    return dict(record)

def update_pin(clip: Clip, clip_id: int | None = None) -> None:

    if clip_id is None or clip_id == 0:
        return None
    pin_status = 1 if clip.is_pinned else 0
    conn = get_connection()
    conn.execute("UPDATE clips SET isPinned = ? WHERE clipID = ? ", (pin_status, clip_id))


    conn.execute("UPDATE")
def read_all_records() -> list[dict] | None:
    conn = get_connection()

    result = conn.execute("SELECT * FROM clips")

    records = result.fetchall()

    if not records:
        return None

    return [dict(r) for r in records]
    

def delete_record(clip_id: int) -> dict | None:
    """removes a record form database , returns the deleted record as dict"""
    conn = get_connection()

    record = read_record(clip_id)
    if record is None:
        return None

    conn.execute("DELETE FROM clips where clipID = ?", (clip_id,))
    conn.commit()

    return record

def add_clip_to_db(clip: Clip | TextClip | AudioClip | ImageClip | VideoClip | OtherClip) -> None:
    """adds a clip object to the database"""
    add_record(clip.get_unique_id(), clip.clip_type, clip.is_pinned, clip.clip_path, clip.clip_data)


def remove_clip_from_db(clip_id: int):
    """removes a clip object"""
    delete_record(clip_id)


def init() -> bool:
    """runs proper proceedings to setup database"""
    global _initialized
    if _initialized:
        return True

    try:
        create_dir(get_data_dir())
        create_dir(get_db_dir())
        create_db()
        _initialized = True
        return True
    except (sqlite3.Error, OSError, PermissionError) as e:
        print(f"[Error] failed to initialize : {e}", file=sys.stderr)
        _initialized = False
        return False


if __name__ == "storeengine":
    """ try to run init any time imported """
    init()
