import re
from dataclasses import dataclass
from io import TextIOWrapper
from os import PathLike
from typing import List, Tuple, Self, Union

from pyosutools.beatmaps.datatypes import (GeneralSettings, EditorSettings, Metadata, Difficulty,
                                           BaseEvent, TimingPoint, ComboColors, BaseHitObject, HitObjectType,
                                           EventType, BackgroundEvent, BreakEvent, VideoEvent,
                                           CircleObject, ManiaHoldObject, SliderObject, SpinnerObject,
                                           SliderType, CurvePoint, HitSound, HitSample)
from pyosutools.utils import is_int


@dataclass
class Beatmap:
    version: int
    general_settings: GeneralSettings
    editor_settings: EditorSettings
    metadata: Metadata
    difficulty: Difficulty
    events: List[BaseEvent]
    timing_points: List[TimingPoint]
    colours: list[ComboColors]
    hit_objects: list[BaseHitObject]

    @staticmethod
    def from_path(path: Union[str, PathLike]) -> Self:
        with open(path, "r") as f:
            return Beatmap.from_file(f)

    @staticmethod
    def from_file(file: TextIOWrapper) -> Self:
        return Beatmap.from_data(file.readlines())

    @staticmethod
    def from_data(data: List[str]) -> Self:
        return _Parser.parse(data)


SECTIONS = [
    "General",
    "Editor",
    "Metadata",
    "Difficulty",
    "Events",
    "TimingPoints",
    "Colours",
    "HitObjects"
]


class _Parser:

    @staticmethod
    def check_header(text):
        for section in SECTIONS:
            if re.match(rf".{section}.", text):
                return section
        return None

    @staticmethod
    def parse_line_with_key(text: str) -> Tuple[str, str]:
        """
        Returns painr (key, value)
        """
        tmp = text.replace("\n", "").split(":")
        tmp = list(map(lambda x: x.lstrip().rstrip(), tmp))
        tmp[0] = "_".join(map(lambda x: x.lower(), re.findall("[A-Z][^A-Z]*", tmp[0])))
        return tmp

    @staticmethod
    def parse_line_without_key(text: str) -> List[str]:
        return text.replace("\n", "").split(",")

    @staticmethod
    def parse_hit_object(values: List[str]) -> BaseHitObject:
        x = int(values[0])
        y = int(values[1])
        time = int(values[2])
        hit_object_type = HitObjectType(int(values[3]))
        hit_sound = HitSound(int(values[4]))

        hit_sample_data = _Parser.parse_hit_sample_data(values[-1:][0])
        hit_sample = HitSample(**hit_sample_data) if hit_sample_data is not None else None

        hit_object = BaseHitObject(x, y, time, hit_sound, hit_sample)

        if hit_object_type == HitObjectType["CIRCLE"]:
            hit_object = CircleObject(x, y, time, hit_sound, hit_sample)
        elif hit_object_type == HitObjectType["SLIDER"]:
            hit_object = SliderObject(x, y, time, hit_sound, hit_sample, **_Parser.parse_slider_object_data(values[5:-1]))
        elif hit_object_type == HitObjectType["SPINNER"]:
            hit_object = SpinnerObject(x, y, time, hit_sound, hit_sample, **_Parser.parse_spinner_object_data(values[5:-1]))
        elif hit_object_type == HitObjectType["MANIA_HOLD"]:
            hit_object = ManiaHoldObject(x, y, time, hit_sound, hit_sample, **_Parser.parse_mania_hold_object_data(values[5:-1]))

        return hit_object

    @staticmethod
    def parse_slider_object_data(values: List[str]) -> dict:
        values = list(map(lambda x: x.split("|"), values))
        return {
            "curve_type": SliderType(values[0][0]),
            "curve_points": [CurvePoint(value[0], value[1]) for value in values[0][1:]],
            "slides": int(values[1][0]),
            "length": float(values[2][0]) if len(values) > 2 else None,
            "edge_sounds": (values[3][0]) if len(values) > 3 else None,
            "edge_sets": (values[4][0]) if len(values) > 4 else None
        }

    @staticmethod
    def parse_spinner_object_data(values: List[str]) -> dict:
        return {
            "end_time": values[0]
        }

    @staticmethod
    def parse_mania_hold_object_data(values: List[str]) -> dict:
        return {
            "end_time": values[0]
        }

    @staticmethod
    def parse_event(values: List[str]) -> BaseEvent:
        event_type = EventType(int(values[0])) if is_int(values[0]) else None
        if event_type is None:
            return None

        start_time = int(values[1])

        if event_type == EventType["BACKGROUND"]:
            hit_object = BackgroundEvent(start_time, **_Parser.parse_background_event_data(values[2:]))

        if event_type == EventType["VIDEO"]:
            hit_object = VideoEvent(start_time, **_Parser.parse_video_event_data(values[2:]))

        if event_type == EventType["BREAK"]:
            hit_object = BreakEvent(start_time, **_Parser.parse_background_event_data(values[2:]))

        return hit_object

    @staticmethod
    def parse_background_event_data(values: List[str]) -> dict:
        return {
            "filename": values[0],
            "x_offset": int(values[1]),
            "y_offset": (values[2])
        }

    @staticmethod
    def parse_video_event_data(values: List[str]) -> dict:
        return {
            "filename": values[0],
            "x_offset": int(values[1]),
            "y_offset": (values[2])
        }

    @staticmethod
    def parse_break_event_data(values: List[str]) -> dict:
        return {
            "end_time": int(values[0])
        }

    @staticmethod
    def parse_hit_sample_data(value: str) -> dict:
        value = value.split(":")
        return {
            "normal_set": int(value[0]),
            "addition_set": int(value[1]),
            "index": int(value[2]),
            "volume": int(value[3]),
            "filename": value[4],
        } if len(value) == 5 else None

    @staticmethod
    def parse(data: List[str]) -> Beatmap:
        version = 0
        general_dict = {}
        editor_dict = {}
        metadata_dict = {}
        difficulty_dict = {}
        events_list = []
        timing_points_list = []
        colours_dict = {"combo": {}}
        hit_objects_list = []
        key = None
        curr_header = None

        for line in data:
            if line == "\n" or line == "":
                continue
            if line.startswith("osu file format"):
                version = int(line.split(" ")[-1:][0][1:])
                continue
            header = _Parser.check_header(line)
            if header is not None:
                curr_header = header
                continue

            if curr_header == "General":
                key, value = _Parser.parse_line_with_key(line)
                general_dict[key] = int(value) if is_int(value) else value
                continue

            elif curr_header == "Editor":
                key, value = _Parser.parse_line_with_key(line)
                editor_dict[key] = int(value) if is_int(value) else value
                continue

            elif curr_header == "Metadata":
                key, value = _Parser.parse_line_with_key(line)
                key = key.replace("i_d", "id")
                metadata_dict[key] = int(value) if is_int(value) else value
                continue

            elif curr_header == "Difficulty":
                key, value = _Parser.parse_line_with_key(line)
                key = key.replace("h_p", "hp")
                difficulty_dict[key] = int(value) if is_int(value) else value
                continue

            elif curr_header == "Events":
                values = _Parser.parse_line_without_key(line)

                event = _Parser.parse_event(values)
                if event is not None:
                    events_list.append(event)
                continue

            elif curr_header == "TimingPoints":
                values = _Parser.parse_line_without_key(line)
                timing_points_list.append(TimingPoint(int(values[0]), float(values[1]), int(values[2]),
                                                      int(values[3]), int(values[4]), int(values[5]), bool(values[6]),
                                                      int(values[7])))
                continue

            elif curr_header == "Colours":
                key, value = _Parser.parse_line_with_key(line)
                if re.match("combo.*", key):
                    colours_dict["combo"][int(key.lstrip("combo"))] = list(map(lambda x: int(x), value.split(",")))
                    continue
                colours_dict[key] = value
                continue

            elif curr_header == "HitObjects":
                values = _Parser.parse_line_without_key(line)

                hit_objects_list.append(_Parser.parse_hit_object(values))
                continue

        return Beatmap(version,
                       GeneralSettings(**general_dict),
                       EditorSettings(**editor_dict),
                       Metadata(**metadata_dict),
                       Difficulty(**difficulty_dict),
                       events_list,
                       timing_points_list,
                       colours_dict,
                       hit_objects_list,)
