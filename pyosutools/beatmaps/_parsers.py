from __future__ import annotations
import re
from typing import List, Tuple, Union, Any

from pyosutools.datatypes import (GeneralSettings, EditorSettings, Metadata, Difficulty,
                                  BaseEvent, BeatmapTimingPoint, ComboColors, BaseHitObject, HitObjectType,
                                  EventType, BackgroundEvent, BreakEvent, VideoEvent,
                                  CircleObject, ManiaHoldObject, SliderObject, SpinnerObject,
                                  SliderType, CurvePoint, HitSound, HitSample)
from pyosutools.utils import is_number, as_number
import pyosutools.beatmaps.beatmap


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


class BaseParser:
    @staticmethod
    def get_version(data: List[str]) -> Union[int, None]:
        for line in data:
            version = UniversalParser.get_version(line)
            if version is not None:
                break

    @staticmethod
    def get_header(text: str) -> Union[str, None]:
        return next((section for section in SECTIONS.ALL if text == section), None)

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


class GeneralParser(BaseParser):
    @staticmethod
    def parse(data: List[str]) -> GeneralSettings:
        header = None

        tmp_settings = GeneralSettings()

        for start_index, line in enumerate(data, 1):
            header = GeneralParser.get_header(line)
            if header == SECTIONS.GENERAL:
                break

        for line in data[start_index:]:
            header = GeneralParser.get_header(line)
            if header != SECTIONS.GENERAL and header is not None:
                break

            if line == "":
                continue

            if line.startswith("//"):
                continue

            key, value = GeneralParser.parse_key_value(line)
            setattr(tmp_settings, key, value)

        return tmp_settings


class EditorParser(BaseParser):
    @staticmethod
    def parse(data: List[str]) -> EditorSettings:
        header = None

        tmp_settings = EditorSettings()

        for start_index, line in enumerate(data, 1):
            header = EditorParser.get_header(line)
            if header == SECTIONS.EDITOR:
                break

        for line in data[start_index:]:
            header = EditorParser.get_header(line)
            if header != SECTIONS.EDITOR and header is not None:
                break

            if line == "":
                continue

            if line.startswith("//"):
                continue

            key, value = EditorParser.parse_key_value(line)
            value = as_number(value) if is_number(value) else value
            setattr(tmp_settings, key, value)

        return tmp_settings


class MetadataParser(BaseParser):
    @staticmethod
    def parse(data: List[str]) -> Metadata:
        header = None

        tmp_settings = Metadata()

        for start_index, line in enumerate(data, 1):
            header = MetadataParser.get_header(line)
            if header == SECTIONS.METADATA:
                break

        for line in data[start_index:]:
            header = MetadataParser.get_header(line)
            if header != SECTIONS.METADATA and header is not None:
                break

            if line == "":
                continue

            if line.startswith("//"):
                continue

            key, value = MetadataParser.parse_key_value(line)
            setattr(tmp_settings, key, value)

        return tmp_settings


class DifficultyParser(BaseParser):
    @staticmethod
    def parse(data: List[str]) -> Difficulty:
        header = None

        tmp_settings = Difficulty()

        for start_index, line in enumerate(data, 1):
            header = DifficultyParser.get_header(line)
            if header == SECTIONS.DIFFICULTY:
                break

        for line in data[start_index:]:
            header = DifficultyParser.get_header(line)
            if header != SECTIONS.DIFFICULTY and header is not None:
                break

            if line == "":
                continue

            if line.startswith("//"):
                continue

            key, value = DifficultyParser.parse_key_value(line)
            setattr(tmp_settings, key, value)

        return tmp_settings


class EventParser(BaseParser):
    @staticmethod
    def parse(data: List[str]) -> list[BaseEvent]:
        tmp_events = []

        for start_index, line in enumerate(data, 1):
            header = EventParser.get_header(line)
            if header == SECTIONS.EVENT:
                break

        for line in data[start_index:]:
            header = EventParser.get_header(line)
            if header != SECTIONS.EVENT and header is not None:
                break

            if line == "":
                continue

            if line.startswith("//"):
                continue

            values = EventParser.parse_values(line)

            # all storyboard events starts with string
            if type(values[0]) is str:
                # TODO add storyboard parsing
                continue

            event_type = EventType(values[0])
            if event_type is None:
                continue

            start_time = values[1]

            if event_type == EventType["BACKGROUND"]:
                tmp_events.append(BackgroundEvent(start_time, **EventParser.parse_background_event(values[2:])))

            elif event_type == EventType["VIDEO"]:
                tmp_events.append(VideoEvent(start_time, **EventParser.parse_video_event(values[2:])))

            elif event_type == EventType["BREAK"]:
                tmp_events.append(BreakEvent(start_time, **EventParser.parse_break_event(values[2:])))

        return tmp_events

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


class TimingPointsParser(BaseParser):
    @staticmethod
    def parse(data: List[str]) -> List[BeatmapTimingPoint]:
        tmp_timing_points = []

        for start_index, line in enumerate(data, 1):
            header = TimingPointsParser.get_header(line)
            if header == SECTIONS.TIMINGPOINTS:
                break

        for line in data[start_index:]:
            header = TimingPointsParser.get_header(line)
            if header != SECTIONS.TIMINGPOINTS and header is not None:
                break

            if line == "":
                continue

            if line.startswith("//"):
                continue

            values = TimingPointsParser.parse_values(line)

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


class ColoursParser(BaseParser):
    @staticmethod
    def parse(data: List[str]) -> ComboColors:
        tmp_combo = ComboColors([])

        for start_index, line in enumerate(data, 1):
            header = ColoursParser.get_header(line)
            if header == SECTIONS.COLOURS:
                break

        for line in data[start_index:]:
            header = ColoursParser.get_header(line)
            if header != SECTIONS.COLOURS and header is not None:
                break

            if line == "":
                continue

            if line.startswith("//"):
                continue

            key, value = ColoursParser.parse_key_value(line)

            if re.fullmatch(".*[1-9]", key):
                tmp_combo.combo.append([int(color) for color in value.split(",")])
            else:
                setattr(tmp_combo, key, [int(color) for color in value.split(",")])

        return tmp_combo


class HitObjectsParser(BaseParser):
    @staticmethod
    def parse(data: List[str]) -> list[BaseHitObject]:
        tmp_objects = []

        for start_index, line in enumerate(data, 1):
            header = HitObjectsParser.get_header(line)
            if header == SECTIONS.HITOBJECTS:
                break

        for line in data[start_index:]:
            header = HitObjectsParser.get_header(line)
            if header != SECTIONS.HITOBJECTS and header is not None:
                break

            if line == "":
                continue

            if line.startswith("//"):
                continue

            values = HitObjectsParser.parse_values(line)

            object_type = HitObjectType(values[0])
            if object_type is None:
                continue

            x, y, time, object_type, hit_sound = values[:5]

            object_type = HitObjectType(object_type)
            new_combo = HitObjectType["NEW_COMBO"] in object_type
            combo_skips = object_type - HitObjectType(143) + HitObjectType(112) if object_type > 30 else 0

            hit_sample = HitObjectsParser.parse_hit_sample(values[-1:][0]) if type(values[-1:][0]) == str and values[-1:][0].count(":") == 4 else None

            if HitObjectType["CIRCLE"] in object_type:
                tmp_objects.append(CircleObject(x, y, time, hit_sound, hit_sample,
                                                new_combo=new_combo,
                                                combo_skips=combo_skips))

            elif HitObjectType["SLIDER"] in object_type:
                tmp_objects.append(SliderObject(x, y, time, hit_sound, **HitObjectsParser.parse_slider(values[5:-1]), hit_sample=hit_sample,
                                                new_combo=new_combo,
                                                combo_skips=combo_skips))

            elif HitObjectType["SPINNER"] in object_type:
                tmp_objects.append(SpinnerObject(x, y, time, hit_sound, **HitObjectsParser.parse_spinner(values[5:-1]), hit_sample=hit_sample,
                                                 new_combo=new_combo,
                                                 combo_skips=combo_skips))

            elif HitObjectType["MANIA_HOLD"] in object_type:
                tmp_objects.append(ManiaHoldObject(x, y, time, hit_sound, **HitObjectsParser.parse_hold(values[5:-1]), hit_sample=hit_sample,
                                                   new_combo=new_combo,
                                                   combo_skips=combo_skips))

        return tmp_objects

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


class UniversalParser(BaseParser):
    @staticmethod
    def parse(data: List[str], format_ver: int = -1) -> pyosutools.beatmaps.beatmap.Beatmap:
        version = format_ver
        if version != -1:
            version = UniversalParser.get_version(data)

        general_settings = GeneralParser.parse(data)
        editor_settings = EditorParser.parse(data)
        metadata = MetadataParser.parse(data)
        difficulty = DifficultyParser.parse(data)
        events = EventParser.parse(data)
        timing_points = TimingPointsParser.parse(data)
        colours = ColoursParser.parse(data)
        hit_objects = HitObjectsParser.parse(data)

        return pyosutools.beatmaps.beatmap.Beatmap(version, general_settings, editor_settings, metadata, difficulty, events, timing_points, colours, hit_objects)
