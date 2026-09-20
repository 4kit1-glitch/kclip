"""
Manager module for kclip
    - contains clip class
    - contains specific class type subclasses
    - contains other general functions

"""

import sys
import hashlib
from datetime import datetime
from typing import ClassVar
from pathlib import Path


PROGRAM_PATH = __file__


class Clip:
    """clip class specifies behaviors and attribute of a clipped item"""

    ALLOWED_TYPES = ("text", "img", "video", "audio", "other")
    MAX_CLIPS: ClassVar[int] = 10
    CLIP_COUNT: ClassVar[int] = 0
    all_clips: ClassVar[list[str]] = []

    def __init__(
        self,
        clip_data: str,
        clip_type: str = "text",
        clip_path: Path | str | None = None,
        date_clipped: datetime | None = None,
        is_pinned: bool = False,
    ) -> None:

        self.clip_type = clip_type
        self.clip_path = clip_path
        self.date_clipped = date_clipped
        self.is_pinned = is_pinned
        self.clip_data = clip_data

    def is_type(self):
        return self.clip_type.strip().lower() in self.ALLOWED_TYPES

    def toggle_pin(self):
        self.is_pinned = not self.is_pinned
        return self.is_pinned

    def get_unique_id(self) -> str:
        """generate unique id from data"""
        TYPE_MAP = {"text": "t", "img": "i", "video": "v", "audio": "a", "other": "o"}
        try:
            id_bytes = self.clip_data.encode()
            id_hash = str(
                int(hashlib.sha256(id_bytes).hexdigest(), 16)
            )  # hash and convert the hash string to into str(numbers)
        except UnicodeEncodeError:
            print(
                "[error] failed to encode", file=sys.stderr
            )  # will modify later to a log file
            return f"{self.clip_data[:3]}F"

        return f"{id_hash[:3]}{TYPE_MAP[self.clip_type]}{id_hash[1]}"

    @classmethod
    def add_clip(cls, clip_obj: "Clip") -> str:
        """add a new clip return unique id of clip via unique_id"""
        unique_id = clip_obj.get_unique_id()

        if unique_id in cls.all_clips:  # fail sfe to catch dublicate cliped items
            return unique_id

        if not isinstance(clip_obj, Clip):
            raise TypeError

        if cls.CLIP_COUNT >= cls.MAX_CLIPS:
            del cls.all_clips[0]
            cls.CLIP_COUNT = len(cls.all_clips)

        if cls.CLIP_COUNT < cls.MAX_CLIPS:
            cls.all_clips.append(clip_obj.get_unique_id())
            cls.CLIP_COUNT += 1

        return unique_id

    @classmethod
    def remove_clip(cls, unique_id: str) -> str:
        """remove a given clip with a unique id"""
        try:
            cls.all_clips.remove(unique_id)
            cls.CLIP_COUNT -= 1
        except ValueError:
            print(f"Failed to remove clip ID{unique_id}", file=sys.stderr)
        return unique_id


class TextClip(Clip):
    """specific class to text clips"""

    def __init__(
        self,
        clip_data: str,
        clip_type: str = "text",
        clip_path: Path | str | None = None,
        date_clipped: datetime | None = None,
        is_pinned: bool = False,
    ) -> None:
        super().__init__(clip_data, clip_type, clip_path, date_clipped, is_pinned)

        self.clip_name = self.clip_data[:15]


class ImageClip(Clip):
    """specific class to imageclips"""

    def __init__(
        self,
        clip_data: str,
        clip_type: str = "img",
        clip_path: Path | str | None = None,
        date_clipped: datetime | None = None,
        is_pinned: bool = False,
    ) -> None:
        super().__init__(clip_data, clip_type, clip_path, date_clipped, is_pinned)

        self.clip_name = f"[IMG]{self.clip_path}"


class AudioClip(Clip):
    """specific class to audio clips"""

    def __init__(
        self,
        clip_data: str,
        clip_type: str = "audio",
        clip_path: Path | str | None = None,
        date_clipped: datetime | None = None,
        is_pinned: bool = False,
    ) -> None:
        super().__init__(clip_data, clip_type, clip_path, date_clipped, is_pinned)

        self.clip_name = f"[AUDIO]{self.clip_path}"


class VideoClip(Clip):
    """specific class to video clips"""

    def __init__(
        self,
        clip_data: str,
        clip_type: str = "video",
        clip_path: Path | str | None = None,
        date_clipped: datetime | None = None,
        is_pinned: bool = False,
    ) -> None:
        super().__init__(clip_data, clip_type, clip_path, date_clipped, is_pinned)

        self.clip_name = f"[VIDEO]{self.clip_path}"

class OtherClip(Clip):
    def __init__(self, clip_data: str, clip_type: str = "other", clip_path: Path | str | None = None, date_clipped: datetime | None = None, is_pinned: bool = False) -> None:
        super().__init__(clip_data, clip_type, clip_path, date_clipped, is_pinned)
        self.clip_name = f"[OTHER]{self.clip_path}"