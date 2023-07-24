from __future__ import annotations
from dataclasses import dataclass
from io import TextIOWrapper
from os import PathLike
from typing import List, Union

from pyosutools.beatmaps.datatypes import (GeneralSettings, EditorSettings, Metadata, Difficulty,
                                           BaseEvent, TimingPoint, ComboColors, BaseHitObject)
import pyosutools.beatmaps._parsers


@dataclass
class Beatmap:
    version: int
    general_settings: GeneralSettings
    editor_settings: EditorSettings
    metadata: Metadata
    difficulty: Difficulty
    events: List[BaseEvent]
    timing_points: List[TimingPoint]
    colours: List[ComboColors]
    hit_objects: List[BaseHitObject]

    @staticmethod
    def from_path(path: Union[str, PathLike], format_ver: int = -1) -> Beatmap:
        with open(path, "r") as file:
            return Beatmap.from_file(file, format_ver)

    @staticmethod
    def from_file(file: TextIOWrapper, format_ver: int = -1) -> Beatmap:
        return Beatmap.from_data(file.readlines(), format_ver)

    @staticmethod
    def from_data(data: List[str], format_ver: int = -1) -> Beatmap:
        data = list(map(lambda x: x.rstrip("\n"), data))
        return pyosutools.beatmaps._parsers.UniversalParser.parse(data, format_ver)
