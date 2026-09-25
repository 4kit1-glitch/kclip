"""
TUI  for kclip uses curses to draw scrollable table of clips stored in the database

"""


import sqlite3
import curses
from .clipfile_link import see_saved, pin, unpin, delete, reset
from .clipmanager import Clip, TextClip, AudioClip, VideoClip, OtherClip, ImageClip

_CLIP_CLASSES = {
    "text": TextClip,
    "img": ImageClip,
    "audio": AudioClip,
    "video": VideoClip,
    "other": OtherClip
}


def _row_to_clip(row: dict) -> Clip:
    """ builds a Clip instance from Database role
    -> work around for v1
    """
    ctype = str(row.get("clipType") or "other").lower()
    cls = _CLIP_CLASSES.get(ctype, OtherClip)

    # setup a clip instance
    clip = cls(
        clip_data = row.get("clipData") or "",
        clip_path = row.get("clipPath"), 
        is_pinned = bool(row.get("isPinned", 0))
    )
    clip.clip_id = row.get("clipID", 0)
    clip.date_clipped = row.get("dateClipped")
    return clip

class ClipTui:
    """
    The main tui controller.

    Holds the current list of clips(mirrored from  the DB)

    """
    def __init__(self, stdscr) -> None:
        self.stdscr = stdscr

        # sets arror keys
        self.stdscr.keypad(True)

        # making colour output
        curses.curs_set(0)
        curses.start_color()

        # using terminal default colours
        curses.use_default_colors()

        # colour pairs for id, forground and background
        curses.init_pair(1, curses.COLOR_CYAN, -1)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(3, curses.COLOR_YELLOW, -1)
        curses.init_pair(4, curses.COLOR_RED, -1)

        self.items = []
        self.selected_idx = 0
        self.offset = 0
        self.status = ""

        self.reload() # this makes sure the db is read at each run instance

    def reload(self):
        """ Pulls records from database so as to composite screen"""

        try:
            records = see_saved() or []
        except sqlite3.Error as e:
            # make sure doesnt crash if database is not set or querry fails
            records = []
            self.status = f"DB error: {e}"
            

