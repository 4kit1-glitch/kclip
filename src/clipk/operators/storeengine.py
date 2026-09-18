import os
import sys
import atexit
import sqlite3
import pyperclip
from PIL import ImageGrab
from pathlib import Path
from clipmanager import Clip, TextClip, AudioClip, ImageClip, VideoClip



APP_NAME = "kclip"
DATABASE_NAME = "kclip.db"

_conn = None
_initialized = False


        

def get_data_dir() -> Path:
    """ returns linux standard data dir"""
    xdg_data_home = os.environ.get("XDG_DATA_HOME")
    if xdg_data_home:
        data_dir = Path(xdg_data_home) / APP_NAME / "data"
    else:
        data_dir = Path.home() / ".local"/ "share" / APP_NAME / "data"
    return data_dir

def get_db_dir() -> Path:
    """ returns the path of database"""
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
        _conn.execute("PRAGMA journal_mode=WAL") # this ensures the database doesnt crash on simultanuous reads
        atexit.register(close_db)
        _conn.row_factory = sqlite3.Row
    return _conn

        

def create_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)
    

def create_db() -> None:
    """ creates the kclip database """

    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS clips (
            clipID INTEGER PRIMARY KEY AUTOINCREMENT,
            uniqueName TEXT NOT NULL,
            clipPath TEXT, 
            isPinned INTEGER NOT NULL, 
            dateClipped TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
    """)


def add_record(unique_name: str, clip_path: Path, is_pinned: bool) -> None:
    """ adds a record to database """
    pinstatus = 1 if is_pinned else 0

    conn = get_connection()

    conn.execute(
        "INSERT INTO clips (uniqueName, clipPath, isPinned) VALUES (?, ?, ?)", 
        (unique_name, str(clip_path), pinstatus)
    )
    conn.commit()


def read_record(clip_id: int| None = None, unique_name: str | None = None) -> dict | None:
    """ reads a specific record from database provided with either the clip_id or
        unique_name
    """
    conn = get_connection()
    if clip_id is not None:
        result = conn.execute(" SELECT * FROM clips WHERE clipID = ?", (clip_id,))
    elif unique_name is not None:
        result = conn.execute(" SELECT * FROM clips WHERE uniqueName = ?", (unique_name,))
    else:
        result = None

    if result is not None:
        return dict(result.fetchone())
    return result


            
        
def delete_record(clip_id: int) -> dict | None:
    """ removes a record form database , returns the deleted record as dict """
    conn = get_connection()

    record = read_record(clip_id)
    if record is None:
        return None
    
    conn.execute(
        "DELETE FROM clips where clipID = ?", (clip_id,)
    )
    conn.commit()

    return record



def add_clip_to_db(clip: Clip):
    # calls add record on the clip
    pass


def remove_clip_from_db():
    # calls delete record
    pass




## working with actual data\
def save_data():
    # function saves the data to data location 
    # correctly parses the type of data and performs its path and performs move
    # or dow

    pass
def save_from_imagegrap():
    """ perform saving of file gotten from PIL.ImageGrap"""

def delete_file():
    pass
def move_file():
    pass

def download():
    pass

print(get_data_dir(), get_db_path())