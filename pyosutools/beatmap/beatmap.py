from __future__ import annotations
from dataclasses import dataclass
from io import TextIOWrapper
from os import PathLike
from typing import List, Union, Tuple, Any
import re

from pyosutools.datatypes import (GeneralSettings, EditorSettings, Metadata, Difficulty,
                                  BaseEvent, BeatmapTimingPoint, ComboColors, BaseHitObject,
                                  HitObjectType, EventType, BackgroundEvent, BreakEvent, VideoEvent,
                                  CircleObject, ManiaHoldObject, SliderObject, SpinnerObject,
                                  SliderType, CurvePoint, HitSound, HitSample)
from pyosutools.utils import is_number, as_number


@dataclass
class Beatmap:
    version: int
    general_settings: GeneralSettings
    editor_settings: EditorSettings
    metadata: Metadata
    difficulty: Difficulty
    events: List[BaseEvent]
    timing_points: List[BeatmapTimingPoint]
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
        return _Parser(data).parse(format_ver)


class _Parser:
    class SECTIONS:
        GENERAL = "[General]"
        EDITOR = "[Editor]"
        METADATA = "[Metadata]"
        DIFFICULTY = "[Difficulty]"
        EVENT = "[Events]"
        TIMINGPOINTS = "[TimingPoints]"
        COLOURS = "[Colours]"
        HITOBJECTS = "[HitObjects]"

        ALL = [GENERAL, EDITOR, METADATA, DIFFICULTY, EVENT,
               TIMINGPOINTS, COLOURS, HITOBJECTS]

    def __init__(self, data) -> None:
        self.data = data

    def parse(self, version):
        if version == -1:
            for line in self.data:
                version_line = line
                if version_line not in {"", " ", "\n"} and version_line.startswith("osu file format"):
                    version = self.get_version(version_line)
                    break

        general_settings = self.parse_general()
        editor_settings = self.parse_editor()
        metadata = self.parse_metadata()
        difficulty = self.parse_difficulty()
        events = self.parse_events()
        timing_points = self.parse_timing_points()
        colours = self.parse_colours()
        hit_objects = self.parse_hit_objects()

        return Beatmap(version, general_settings, editor_settings, metadata, difficulty, events, timing_points, colours, hit_objects)

    def parse_general(self) -> GeneralSettings:
        header = None

        tmp_general = GeneralSettings()

        for start_index, line in enumerate(self.data, 1):
            header = self.get_header(line)
            if header == self.SECTIONS.GENERAL:
                break

        for line in self.data[start_index:]:
            header = self.get_header(line)
            if header != self.SECTIONS.GENERAL and header is not None:
                break

            if line == "":
                continue

            if line.startswith("//"):
                continue

            key, value = self.parse_key_value(line)
            setattr(tmp_general, key, value)

        return tmp_general

    def parse_editor(self) -> EditorSettings:
        header = None

        tmp_editor = EditorSettings()

        for start_index, line in enumerate(self.data, 1):
            header = self.get_header(line)
            if header == self.SECTIONS.EDITOR:
                break

        for line in self.data[start_index:]:
            header = self.get_header(line)
            if header != self.SECTIONS.EDITOR and header is not None:
                break

            if line == "":
                continue

            if line.startswith("//"):
                continue

            key, value = self.parse_key_value(line)
            value = as_number(value) if is_number(value) else value
            setattr(tmp_editor, key, value)

        return tmp_editor

    def parse_metadata(self) -> Metadata:
        header = None

        tmp_metadata = Metadata()

        for start_index, line in enumerate(self.data, 1):
            header = self.get_header(line)
            if header == self.SECTIONS.METADATA:
                break

        for line in self.data[start_index:]:
            header = self.get_header(line)
            if header != self.SECTIONS.METADATA and header is not None:
                break

            if line == "":
                continue

            if line.startswith("//"):
                continue

            key, value = self.parse_key_value(line)
            setattr(tmp_metadata, key, value)

        return tmp_metadata

    def parse_difficulty(self) -> Difficulty:
        header = None

        tmp_difficulty = Difficulty()

        for start_index, line in enumerate(self.data, 1):
            header = self.get_header(line)
            if header == self.SECTIONS.DIFFICULTY:
                break

        for line in self.data[start_index:]:
            header = self.get_header(line)
            if header != self.SECTIONS.DIFFICULTY and header is not None:
                break

            if line == "":
                continue

            if line.startswith("//"):
                continue

            key, value = self.parse_key_value(line)
            setattr(tmp_difficulty, key, value)

        return tmp_difficulty

    def parse_events(self) -> list[BaseEvent]:
        tmp_events = []

        for start_index, line in enumerate(self.data, 1):
            header = self.get_header(line)
            if header == self.SECTIONS.EVENT:
                break

        for line in self.data[start_index:]:
            header = self.get_header(line)
            if header != self.SECTIONS.EVENT and header is not None:
                break

            if line == "":
                continue

            if line.startswith("//"):
                continue

            values = self.parse_values(line)

            # all storyboard events starts with string
            if type(values[0]) is str:
                # TODO add storyboard parsing
                continue

            event_type = EventType(values[0])
            if event_type is None:
                continue

            start_time = values[1]

            if event_type == EventType["BACKGROUND"]:
                tmp_events.append(BackgroundEvent(start_time, **self.parse_background_event(values[2:])))

            elif event_type == EventType["VIDEO"]:
                tmp_events.append(VideoEvent(start_time, **self.parse_video_event(values[2:])))

            elif event_type == EventType["BREAK"]:
                tmp_events.append(BreakEvent(start_time, **self.parse_break_event(values[2:])))

        return tmp_events

    def parse_timing_points(self) -> List[BeatmapTimingPoint]:
        tmp_timing_points = []

        for start_index, line in enumerate(self.data, 1):
            header = self.get_header(line)
            if header == self.SECTIONS.TIMINGPOINTS:
                break

        for line in self.data[start_index:]:
            header = self.get_header(line)
            if header != self.SECTIONS.TIMINGPOINTS and header is not None:
                break

            if line == "":
                continue

            if line.startswith("//"):
                continue

            values = self.parse_values(line)

            start_time = values[0]
            beat_length = values[1]
            meter = None
            sample_set = None
            uninherited = None
            effects = None

            if len(values) > 2:
                meter = values[2]
                sample_set = HitSample(values[3], None, values[4], values[5], None)
                uninherited = values[6]
                effects = values[7] if len(values) > 7 else None

            tmp_timing_points.append(BeatmapTimingPoint(start_time, beat_length, meter, sample_set, uninherited, effects))

        return tmp_timing_points

    def parse_colours(self) -> ComboColors:
        tmp_combo = ComboColors([])

        for start_index, line in enumerate(self.data, 1):
            header = self.get_header(line)
            if header == self.SECTIONS.COLOURS:
                break

        for line in self.data[start_index:]:
            header = self.get_header(line)
            if header != self.SECTIONS.COLOURS and header is not None:
                break

            if line == "":
                continue

            if line.startswith("//"):
                continue

            key, value = self.parse_key_value(line)

            if re.fullmatch(".*[1-9]", key):
                tmp_combo.combo.append([int(color) for color in value.split(",")])
            else:
                setattr(tmp_combo, key, [int(color) for color in value.split(",")])

        return tmp_combo

    def parse_hit_objects(self) -> list[BaseHitObject]:
        tmp_objects = []

        for start_index, line in enumerate(self.data, 1):
            header = self.get_header(line)
            if header == self.SECTIONS.HITOBJECTS:
                break

        for line in self.data[start_index:]:
            header = self.get_header(line)
            if header != self.SECTIONS.HITOBJECTS and header is not None:
                break

            if line == "":
                continue

            if line.startswith("//"):
                continue

            values = self.parse_values(line)

            object_type = HitObjectType(values[0])
            if object_type is None:
                continue

            x, y, time, object_type, hit_sound = values[:5]

            object_type = HitObjectType(object_type)
            new_combo = HitObjectType["NEW_COMBO"] in object_type
            combo_skips = object_type - HitObjectType(143) + HitObjectType(112) if object_type > 30 else 0

            hit_sample = self.parse_hit_sample(values[-1:][0]) if type(values[-1:][0]) == str and values[-1:][0].count(":") == 4 else None

            if HitObjectType["CIRCLE"] in object_type:
                tmp_objects.append(CircleObject(x, y, time, hit_sound, hit_sample,
                                                new_combo=new_combo,
                                                combo_skips=combo_skips))

            elif HitObjectType["SLIDER"] in object_type:
                tmp_objects.append(SliderObject(x, y, time, hit_sound, **self.parse_slider(values[5:-1]), hit_sample=hit_sample,
                                                new_combo=new_combo,
                                                combo_skips=combo_skips))

            elif HitObjectType["SPINNER"] in object_type:
                tmp_objects.append(SpinnerObject(x, y, time, hit_sound, **self.parse_spinner(values[5:-1]), hit_sample=hit_sample,
                                                 new_combo=new_combo,
                                                 combo_skips=combo_skips))

            elif HitObjectType["MANIA_HOLD"] in object_type:
                tmp_objects.append(ManiaHoldObject(x, y, time, hit_sound, **self.parse_hold(values[5:-1]), hit_sample=hit_sample,
                                                   new_combo=new_combo,
                                                   combo_skips=combo_skips))

        return tmp_objects

    # ----------UNIVERSAL METHODS---------- #
    @staticmethod
    def get_version(text: str) -> Union[int, None]:
        return int(text.split(" ")[-1:][0][1:])

    @staticmethod
    def get_header(text: str) -> Union[str, None]:
        return next((section for section in _Parser.SECTIONS.ALL if text == section), None)

    @staticmethod
    def parse_key_value(text: str) -> Tuple[str, Any]:
        """
        Returns pair (key, value)
        """
        tmp = text.replace("\n", "").split(":")
        key = tmp[0]
        value = ":".join(tmp[1:])
        key, value = key.lstrip().rstrip(), value.lstrip().rstrip()
        key = "_".join(map(lambda x: x.lower(), re.findall("[A-Z][^A-Z]*", key)))  # wtf is that??
        if is_number(value):
            value = as_number(value)
        return key, value

    @staticmethod
    def parse_values(text: str) -> List[Any]:
        return list(map(lambda x: as_number(x) if is_number(x) else x, text.replace("\n", "").split(",")))

    # ------------EVENTS METHODS------------ #
    @staticmethod
    def parse_background_event(values: List[str]) -> dict:
        tmp_dict = {
            "filename": values[0]
        }

        if len(values) > 1:
            tmp_dict.update({
                "x_offset": values[1],
                "y_offset": values[2]})
        return tmp_dict

    @staticmethod
    def parse_video_event(values: List[str]) -> dict:
        tmp_dict = {
            "filename": values[0]
        }

        if len(values) > 1:
            tmp_dict.update({
                "x_offset": values[1],
                "y_offset": values[2]})
        return tmp_dict

    @staticmethod
    def parse_break_event(values: List[str]) -> dict:
        return {
            "end_time": values[0]
        }

    # ----------HIT OBJECT METHODS---------- #
    @staticmethod
    def parse_hit_sample(value: str) -> dict:
        value = value.split(":")
        return {
            "normal_set": value[0],
            "addition_set": value[1],
            "index": value[2],
            "volume": value[3],
            "filename": value[4],
        }

    @staticmethod
    def parse_slider(values: list[Any]) -> dict:
        tmp_dict = {
            "curve_type": SliderType(values[0].split("|")[0]),
            "curve_points": [CurvePoint(int(point.split(":")[0]), int(point.split(":")[1])) for point in values[0].split("|")[1:]],
            "slides": None,
            "length": None,
            "edge_sounds": None,
            "edge_sets": None
        }

        if len(values) > 2:
            tmp_dict.update({
                "slides": values[1],
                "length": values[2]})
        if len(values) > 4:
            tmp_dict.update({
                "edge_sounds": (HitSound(int(value[0])) for value in values[3].split("|")),
                "edge_sets": (HitSample(int(value[0]), int(value[1])) for value in values[4].split("|"))})
        return tmp_dict

    @staticmethod
    def parse_spinner(values: list[Any]) -> dict:
        if len(values) > 1:
            return {
                "end_time": values[0],
            }
        else:
            return {"end_time": None}

    @staticmethod
    def parse_hold(values: list[Any]) -> dict:
        if len(values) > 1:
            return {
                "end_time": values[0],
            }
        else:
            return {"end_time": None}
