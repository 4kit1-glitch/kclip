"""
TUI  for kclip uses curses to draw scrollable table of clips stored in the database

"""

import sqlite3
import curses
from PIL import Image
from .clipfile_link import see_saved, pin, unpin, delete, reset, save
from .clipmanager import Clip, TextClip, AudioClip, VideoClip, OtherClip, ImageClip, read_clipboard

_CLIP_CLASSES = {
    "text": TextClip,
    "img": ImageClip,
    "audio": AudioClip,
    "video": VideoClip,
    "other": OtherClip,
}


def _row_to_clip(row: dict) -> Clip:
    """builds a Clip instance from Database role
    -> work around for v1
    """
    ctype = str(row.get("clipType") or "other").lower()
    cls = _CLIP_CLASSES.get(ctype, OtherClip)

    # setup a clip instance
    clip = cls(
        clip_data=row.get("clipData") or "",
        clip_path=row.get("clipPath"),
        is_pinned=bool(row.get("isPinned", 0)),
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

        self.reload()  # this makes sure the db is read at each run instance

        # add key bindings

        self._KEY_BINDS = {
            curses.KEY_DOWN: self._move_down,
            ord("s"): self._move_down,
            curses.KEY_UP: self._move_up,
            ord("w"): self._move_up,
            ord("r"): self._refresh,
            ord("R"): self._do_reset,
            ord("p"): self._do_pin,
            ord("d"): self._do_delete,
        }

    def reload(self):
        """Pulls records from database so as to composite screen"""

        try:
            records = see_saved() or []
        except sqlite3.Error as e:
            # make sure doesnt crash if database is not set or querry fails
            records = []
            self.status = f"DB error: {e}"

        items = []
        for idx, row in enumerate(records):
            clip = _row_to_clip(row)
            items.append(
                {
                    "id": row.get("clipID", 0),
                    "name": str(getattr(clip, "clip_name", "") or ""),
                    "date": str(row.get("dateClipped", ""))[:19],
                    "type": str(row.get("clipType") or "?")[:8],
                    "pinned": bool(row.get("isPinned", 0)),
                    "clip": clip,
                }
            )

        self.items = items

        if self.selected_idx >= len(self.items):
            self.selected_idx = max(0, len(self.items) - 1)

    def draw(self):
        # full frame
        self.stdscr.erase()
        self._draw_header()
        self._draw_list()
        self._draw_footer()
        self.stdscr.refresh()

    def _draw_header(self):
        """draws headers"""
        _max_y, max_x = self.stdscr.getmaxyx()
        headers = [("ID", 5), ("NAME", 30), ("Date", 20), ("Type", 8), ("Pin", 4)]
        x = 0
        for text, width in headers:
            if x >= max_x:  # guard against narrow terminals
                break
            self.stdscr.addstr(
                0, x, text.ljust(width)[:width], curses.color_pair(1) | curses.A_BOLD
            )
        self.stdscr.addstr(1, 0, "-" * min(x, max_x - 1))

    def _draw_list(self) -> None:
        """draws list of clips"""
        max_y, max_x = self.stdscr.getmaxyx()
        body_top = 2
        body_bottom = max_y - 2
        view_height = body_bottom - body_top

        # fallback when no items found
        if not self.items:
            self.stdscr.addstr(body_top, 0, "No clip saved.")
            return
        for i in range(self.offset, min(len(self.items), self.offset + view_height)):
            item = self.items[i]
            y = body_top + (i - self.offset)

            pin_mark = "*" if item["pinned"] else " "
            name = item["name"][:30]
            row = (
                f"{item['id']:<5}"
                f"{name:<30}"
                f"{item['date']:<20}"
                f"{item['type']:<8}"
                f"{pin_mark:<4}"
            )[: max_x - 1]

            if i == self.selected_idx:
                self.stdscr.addstr(y, 0, row, curses.color_pair(2))
            elif item["pinned"]:
                self.stdscr.addstr(y, 0, row, curses.color_pair(3))
            else:
                self.stdscr.addstr(y, 0, row)

    def _draw_footer(self):
        """draws tui footer"""
        max_y, max_x = self.stdscr.getmaxyx()
        text = (
            self.status
            or "up/down(move) p (pin) d (delete) r (refresh) R (reset) q (quit)"
        )
        attr = curses.color_pair(4) if self.status else curses.A_DIM
        self.stdscr.addstr(max_y - 1, 0, text[: max_x - 1], attr)

    def _refresh(self):
        self.reload()
        self.status = "Refreshed."

    # handling input
    def handle_key(self, key) -> bool:
        """
        Processes one key press
        Returns False to quit
        """
        if key == ord("q"):
            return False

        action = self._KEY_BINDS.get(key)

        if action:
            action()
        else:
            self.status = ""
        return True

    # navigations
    def _move_down(self):
        if self.selected_idx < len(self.items) - 1:
            self.selected_idx += 1
            max_y, _ = self.stdscr.getmaxyx()
            view_hieght = (max_y - 2) - 2
            if self.selected_idx - self.offset >= view_hieght:
                self.offset = self.selected_idx - view_hieght + 1

    def _move_up(self):
        if self.selected_idx > 0:
            self.selected_idx -= 1

        self.offset = min(self.offset, self.selected_idx)

    # actions

    def _current(self):
        if not self.items:
            return None
        return self.items[self.selected_idx]["clip"]

    def _do_pin(self):
        clip = self._current()

        if clip is None:
            return

        try:
            item = self.items[self.selected_idx]
            if item["pinned"]:
                unpin(clip)
                item["pinned"] = False
                item["clip"].is_pinned = False
                self.status = "Unpinned."
            else:
                pin(clip)
                item["pinned"] = True
                item["clip"].is_pinned = True
                self.status = "Pinned."
        except (sqlite3.Error, ValueError, AttributeError) as e:
            self.status = f"Pin failed {e}"

    def _do_delete(self):
        clip = self._current()
        if clip is None:
            return

        try:
            delete(clip)
            self.items.pop(self.selected_idx)
            if self.selected_idx >= max(0, len(self.items)):
                self.selected_idx = max(0, len(self.items) - 1)
            self.status = "Deleted"
        except (sqlite3.Error, OSError, AttributeError) as e:
            self.status = f"Delete failed: {e}"

    def _do_reset(self):
        max_y, max_x = self.stdscr.getmaxyx()
        self.stdscr.addstr(
            max_y - 1,
            0,
            "Reset EVERYTHING (y/N)".ljust(max_x - 1),
            curses.color_pair(4),
        )
        self.stdscr.refresh()

        key = self.stdscr.getch()
        self.stdscr.timeout(POLL_MS)

        if key in (ord("y"), ord("Y")):
            try:
                reset()
                self.items = []
                self.selected_idx = 0
                self.offset = 0
                self.status = "Reset complete"
            except (sqlite3.Error, OSError, AttributeError) as e:
                self.status = f"Reset failed: {e}"
        else:
            self.status = "Reset Cancelled"


POLL_MS = 300 # makes db refesh every ~300ms
CLIP_CHECK_TIME = 3 # check clibords every  0.9 secs


def _clipboard_signature(value):
    if isinstance(value, str):
        return ("str", value)
    if isinstance(value, list):
        return ("list", tuple(map(str, value)))
    if isinstance(value, Image.Image):
        return ("img", value.size, value.mode)
    return ("other", repr(value))


def _build_clip_for(value):
    if isinstance(value, Image.Image):
        return ImageClip(clip_data="")
    return TextClip(clip_data="")


def run_tui():
    """ run the tui """
    def _main(stdscr):
        tui = ClipTui(stdscr)
        stdscr.timeout(POLL_MS)

        last_sig = _clipboard_signature(read_clipboard())
        tick = 0
        running = True

        while running:
            tick += 1

            # clipboard watch (every N ticks)
            if tick % CLIP_CHECK_TIME == 0:
                try:
                    current = read_clipboard()
                    sig = _clipboard_signature(current)
                    if sig != last_sig:
                        save(_build_clip_for(current))
                        last_sig = sig
                except Exception: # never kill the TUI over a clipboard hiccup
                    # catching all exceptions whatsoever
                    pass  
            # refresh + draw
            tui.reload()
            tui.draw()

            # input
            key = stdscr.getch()
            if key == -1:
                continue
            running = tui.handle_key(key)

    curses.wrapper(_main)