"""the link between the clip, database and file"""
import os
import shutil
import subprocess
import pyperclip
from pathlib import Path

from PIL import Image

from .clipmanager import (
    Clip,
    TextClip,
    ImageClip,
    AudioClip,
    OtherClip,
    VideoClip,
    read_clipboard,
    is_single_clip,
)
from .filemanager import (
    copy_file,
    delete_file,
    delete_all_files,
    copy_from_image_grap,
    is_safe_to_copy,
)
from .storeengine import (
    add_clip_to_db,
    remove_clip_from_db,
    delete_db,
    read_all_records,
    update_pin,
)


def save(clip: Clip | TextClip | ImageClip | AudioClip | OtherClip | VideoClip) -> None:
    """perform full save"""
    current_clip = read_clipboard()

    if not is_single_clip(current_clip):
        clip.clip_data = str(current_clip)
        Clip.add_clip(clip)
        add_clip_to_db(clip)
        return None

    if isinstance(current_clip, str):
        clip.clip_data = current_clip
        data = clip.clip_data
        if is_safe_to_copy(data):
            copied_path = copy_file(Path(data), clip)
            clip.clip_path = copied_path
            add_clip_to_db(clip)
            return None
        if isinstance(current_clip, Image.Image):
            copied_path = copy_from_image_grap(current_clip)
            clip.clip_path = copied_path
            add_clip_to_db(clip)
        if isinstance(current_clip, list):
            data = "\n".join(current_clip)
            clip.clip_data = data
            add_clip_to_db(clip)


def see_saved() -> list[dict] | None:
    return read_all_records()


def pin(clip: Clip):
    clip.is_pinned = True
    update_pin(clip, clip.clip_id)


def delete(
    clip: Clip | TextClip | ImageClip | VideoClip | OtherClip | AudioClip,
) -> None:
    remove_clip_from_db(clip.clip_id)
    if clip.clip_path is not None:
        delete_file(clip)


def unpin(clip: Clip):
    clip.is_pinned = False
    update_pin(clip, clip.clip_id)


def reset():
    Clip.remove_all_clips()
    delete_all_files()
    delete_db()


def _copy_by_pyper(item: str) -> bool:
    try:
        pyperclip.copy(item)
        return True
    except pyperclip.PyperclipException:
        return False

def return_to_clipboard(clip: Clip) -> bool:
    """
    Put a saved clip back on the system clipboard.
    - text clips  -> pyperclip
    - file clips  -> wl-copy on Wayland, xclip on X11, path-as-text as last resort
    """
    typ = clip.clip_type
    data = clip.clip_data
    pth = clip.clip_path

    # --- text -------------------------------------------------------
    if typ == "text":
        if not data:
            return False
        return _copy_by_pyper(data)

    # --- file clips need a path -------------------------------------
    if not pth:
        return False

    path = Path(pth)
    if not path.exists():
        return False

    uri = f"file://{path.resolve()}\n"

    session = os.environ.get("XDG_SESSION_TYPE", "").lower()

    if session == "wayland":
        wl_copy = shutil.which("wl-copy")
        if wl_copy is not None:
            try:
                subprocess.run(
                    [wl_copy, "--type", "text/uri-list"],
                    input=uri.encode(),
                    check=True,
                )
                return True
            except (subprocess.CalledProcessError, OSError):
                pass

    xclip = shutil.which("xclip")
    if xclip is not None:
        try:
            subprocess.run(
                [xclip, "-selection", "clipboard", "-t", "text/uri-list", "-i"],
                input=uri.encode(),
                check=True,
            )
            return True
        except (subprocess.CalledProcessError, OSError):
            pass

    return _copy_by_pyper(str(path))
    

    
