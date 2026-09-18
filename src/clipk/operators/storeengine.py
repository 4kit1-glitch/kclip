import os
import sys
import sqlite3
from pathlib import Path

APP_NAME = "kclip"


def get_data_dir() -> Path:
    """ returns linux standard data dir"""
    xdg_data_home = os.environ.get("XDG_DATA_HOME")
    if xdg_data_home:
        data_dir = Path(xdg_data_home) / APP_NAME / "data"
    else:
        data_dir = Path.home() / ".local"/ "share" / APP_NAME / "data"
    
    return data_dir

def get_db_path() -> Path:
    """ returns the path of database"""
    return get_data_dir() / "db" / "kclip.db"


def create_db():
    pass

def add_clip_to_db():
    pass

def remove_clip_from_db():
    pass

def main():
    pass

if __name__ == "__main__":
    main()