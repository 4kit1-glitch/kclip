"""
file processor and storage module
    - file movement
    - file storage
    - database to file linkage
    - major clipbaord manipulation
"""

import os
import sys
import hashlib
from datetime import datetime
from pathlib import Path
from shutil import copy2
from pyperclip import copy, paste
from PIL import ImageGrab, Image
from typing import Any

from storeengine import APP_NAME, get_data_dir, create_dir


VIDEO_EXTS = {".mp4", ".mkv", ".gif", ".mov", ".avi", ".webm"}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
AUDIO_EXTS = {".wav", ".m4a", ".mp3", ".aac"}

MAX_COPY_SIZE = 100 * (1024**2)  # sets max copy size to 100Mb


def get_store_path(clip_type: str) -> Path | None:
    data_dir = get_data_dir()
    match clip_type.lower():
        case "text":
            return None
        case "img":
            return data_dir / "images"
        case "audio":
            return data_dir / "audios"
        case "video":
            return data_dir / "videos"
        case "other":
            return data_dir / "others"
        case _:
            return None


def _get_ext(string: str) -> str:
    """return the extension"""
    return Path(string).suffix.lower()


# test groups
def is_vid(item: str) -> bool:
    return _get_ext(item) in VIDEO_EXTS


def is_audio(item: str) -> bool:
    return _get_ext(item) in AUDIO_EXTS


def is_img(item: str) -> bool:
    return _get_ext(item) in IMAGE_EXTS


def is_text(item: str) -> bool:
    return _get_ext(item) == ""


def is_other(item: str) -> bool:
    return not is_audio(item) or is_img(item) or is_text(item) or is_vid(item)


# path checkers
def is_path(item: str) -> bool:
    """checks if what is clipped is a path"""
    path = Path(item)
    return path.exists()


def is_file(path: str | Path) -> bool:
    """checks if path leads to a file"""
    return Path(path).is_file()


def is_dir(path: str | Path) -> bool:
    """checks if path leads to a dir"""
    return Path(path).is_dir()


def is_mount_point(path_str: str) -> bool:
    """check if copied is a mount point"""
    path = Path(path_str).resolve()

    # this makes sure block devices files are not copied
    if str(path).startswith("/dev/"):
        return True
    return os.path.ismount(path)


def is_absolute(path: Path | str) -> bool:
    return Path(path).is_absolute()


def is_safe_to_copy(path_str: str) -> bool:
    """ensures that what is to be copied and moved is safe"""
    return is_path(path_str) and not is_mount_point(path_str)


# file movement functions
def human_size(n: float) -> float:
    return n / (1024**2)


def get_file_size(file_path: Path) -> int | None:
    try:
        return file_path.stat().st_size
    except OSError:
        return None


def get_file_type(path_str: str) -> str:
    if is_vid(path_str):
        return "video"
    elif is_audio(path_str):
        return "audio"
    elif is_text(path_str):
        return "text"
    elif is_img(path_str):
        return "img"
    else:
        return "other"


def generate_new_file_name(path: Path) -> str:
    """generate file names for moved files"""
    extension = _get_ext(str(path))
    timestamp = datetime.now().astimezone().strftime("%Y%m%d_%H_%M_%S")
    short_hash = hashlib.md5(str(path).encode()).hexdigest()[
        :8
    ]  # generate 8 chr filename
    return f"{timestamp}_{short_hash}{extension}"


def perform_copy(path: Path, path_bytes: int, path_type: str = "other") -> Path | None:
    """
    actual copy proceedings return the destination path
    returns none if no copy was performed

    dest -> destination btw

    """

    # first i get destination folder
    dest_dir = get_store_path(path_type)

    # ensure destination folder is created
    if dest_dir:
        create_dir(dest_dir)
    else:
        return None

    # generate identity name
    identity_name = generate_new_file_name(path)

    # i get destination filepath
    dest_path = dest_dir / identity_name

    if not path_bytes <= MAX_COPY_SIZE:
        return None

    # then i perform copy
    try:
        copy2(path, dest_path)
    except (FileNotFoundError, OSError):
        return None

    return dest_path


def copy_file(path: Path) -> Path | None:
    """
    copies a file from its path to kclip store path
    does copy on files less than 101mb
    """

    path_str = str(path)

    if not is_path(path_str):
        return None

    if not is_file(path):
        return None

    if not is_safe_to_copy(path_str):
        return None

    size = get_file_size(path)

    if size is None or size > MAX_COPY_SIZE:
        return None

    path_type = get_file_type(path_str)

    return perform_copy(path, size, path_type)


def save_as_text(path: Path) -> str | None:
    # fall back to text if copy failed and others failed
    if not copy_file(path):
        return str(path)


def copy_from_image_grap(pil_image: Image.Image) -> Path | None:
    data_type = "img"
    dest_dir = get_store_path(data_type)
    identity = generate_new_file_name(Path("web_clip.png"))
    
    if dest_dir:
        dest_path = dest_dir / identity
    else:
        return None
    
    try:
        create_dir(dest_dir)
        pil_image.save(dest_path)
    except OSError:
        return None
    
    return dest_path


def read_from_image_grap():
    return ImageGrab.grabclipboard()

def read_from_pyperclip() -> str:
    """returns output of paste() from pyperclip"""
    return paste()


def read_clipboard():
    if read_from_image_grap() is None:
        print("p\n", read_from_pyperclip())
        return
    print("I\n", read_from_image_grap())


read_clipboard()
