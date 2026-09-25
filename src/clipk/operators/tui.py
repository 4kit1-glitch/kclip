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

        items = []
        for idx, row in enumerate(records):
            clip = _row_to_clip(row)
            items.append({
                "idx": idx, 
                "id": row.get("clipId", 0),
                "uid": str(row.get("uniqueName", "?"))[:10],
                "date": str(row.get("dataClipped", ""))[:19],
                "type": str(row.get("clipType"))[:8],
                "pinned": bool(row.get("isPinned", 0)),
                "clip": clip
            })

        self.items = items

        if self.selected_idx >= len(self.items):
            self.selected_idx = max(0, len(self.items))


    def draw(self):
        # full frame
        self.stdscr.erase()
        self._draw_header()
        self._draw_list()
        self._draw_footer()
        self.stdscr.refresh()

    def _draw_header(self):
        """ draws headers"""
        _max_y, max_x = self.stdscr.getmaxyx()
        headers = [("ID", 5), ("UID", 12), ("Date", 20), ("Type", 8), ("Pin", 4)]
        x = 0
        for text, width in headers:
            if x >= max_x: # guard against narrow terminals
                break
            self.stdscr.addstr(0, x, text.ljust(width)[:width], curses.color_pair(1) | curses.A_BOLD)
        self.stdscr.addstr(1, 0, "-" * min(x, max_x -1))


    def _draw_list(self) -> None:
        """ draws list of clips"""
        max_y, max_x = self.stdscr.getmaxyx()
        body_top = 2
        body_bottom = max_y - 2
        view_height =body_bottom - body_top

        # fallback when no items found
        if not self.items:
            self.stdscr.addstr(body_top, 0, "No clip saved.")
            return 
        for i in range(self.offset, min(len(self.items), self.offset + view_height)):
            item = self.items[i]
            y = body_top + (i - self.offset)

            pin_mark = "*" if item["pinned"] else " "
            row = (
                f"{item['id']:<5}",
                f"{item['uid']:<5}",
                f"{item['date']:<5}",
                f"{item['type']:<8}",
                f"{pin_mark:<4}"
            )[:max_x - 1]

            if i == self.selected_idx:
                self.stdscr.addstr(y, 0, row, curses.color_pair(2))
            elif item["pinned"]:
                self.stdscr.addstr(y, 0, row, curses.color_pair(3))
            else:
                self.stdscr.addstr(y, 0, row)


    def _draw_footer(self):
        """ draws tui footer"""
        max_y, max_x = self.stdscr.getmaxyx()
        text = self.status or "up/down(move) p (pin) d (delete) r (refresh) R (reset) q (quit)"
        attr = curses.color_pair(4) if self.status else curses.A_DIM
        self.stdscr.addstr(max_y - 1, 0, text[:max_x - 1], attr)

    # handling input
    def handle_key(self, key) -> bool:
        """
        Processes one key press
        Returns False to quit
        """
        return True

