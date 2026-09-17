import os
import sys
from datetime import datetime
import hashlib
from pathlib import Path

import pyperclip



PROGRAM_PATH = __file__

class Clip:
    """ clip class specifies behaviors and attribute of a clipped item """
    ALLOWED_TYPES = ("text", "img", "video")

    def __init__(self, clip_data: str, clip_type: str = "text",
                clip_path: Path | str | None = None,
                date_clipped: datetime | None = None,
                is_pinned: bool = False) -> None:
        
        self.clip_type = clip_type
        self.clip_path = clip_path
        self.date_clipped = date_clipped
        self.is_pinned = is_pinned
        self.clip_data = clip_data

    def is_type(self):
        return self.clip_type.strip().lower() in self.ALLOWED_TYPES

    def pin_clip(self):
        self.is_pinned = True


    def get_unique_id(self) -> str:
        id_bytes = self.clip_data.encode()
        id_hash = str(int(hashlib.sha256(id_bytes).hexdigest(), 16))  # hash and convert the hash string to into str(numbers)

        TYPE_MAP = {"text": "t", "img":"i", "video":"v"}

        return f"{id_hash[:3]}{TYPE_MAP[self.clip_type]}{id_hash[1]}"



class TextClip(Clip):
    def __init__(self, clip_data: str, clip_type: str = "text",
                 clip_path: Path | str | None = None, 
                 date_clipped: datetime | None = None, 
                 is_pinned: bool = False) -> None:
        super().__init__(clip_data, clip_type, clip_path, date_clipped, is_pinned)

    def get_clip_name(self):
        pass

