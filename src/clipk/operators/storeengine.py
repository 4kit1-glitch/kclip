import os
import sys
import sqlite3
import pyperclip
from PIL import ImageGrab
from pathlib import Path
from clipmanager import Clip, TextClip, AudioClip, ImageClip, VideoClip



APP_NAME = "kclip"
DATABASE_NAME = "kclip.db"


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

def create_dir(path: Path) -> int:
    try: 
        path.mkdir(parents=True, exist_ok=True)
    except (OSError, PermissionError):
        print(f"[ERROR] failed to create {path}", file=sys.stderr)
        return 1
    return 0

    

def create_db(db_path: Path) -> None:
    """ creates the kclip database in a provided path """
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS kclip (
                clipID INTEGER PRIMARY KEY AUTOINCREMENT,
                uniqueName TEXT NOT NULL,
                clipPath TEXT, 
                isPinned BOOL NOT NULL, 
                dateClipped TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database Error: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()

def add_record(unique_name: str, clip_path: Path, is_pinned: bool, ):
    # in a try statement
    # do execute insert into database with items from the class
    # then commit and close the changes
    pass

def delete_record():
    pass
    

def add_clip_to_db(clip: Clip):
    # calls add record on the clip
    pass


def remove_clip_from_db():
    # calls delete record
    pass

def read_data(clip_id: int, unique_name: str) -> tuple:
    #goes to data base and reads a specific info 
    # tries and closes databasse after the read
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