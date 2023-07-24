from __future__ import annotations
from dataclasses import dataclass
from aenum import IntFlag, Enum
from typing import List, Tuple

from pyosutools.datatypes import GameMode


class HitObjectType(IntFlag):
    CIRCLE = 1 << 0
    SLIDER = 1 << 1
    NEW_COMBO = 1 << 2
    SPINNER = 1 << 3
    COMBO_SKIP = 7 << 4
    MANIA_HOLD = 1 << 7


class EventType(Enum):
    BACKGROUND = 0
    VIDEO = 1
    BREAK = 2
    BACKGROUND_COLOUR = 3


class HitSound(IntFlag):
    NORMAL = 1 << 0
    WHISTLE = 1 << 1
    FINISH = 1 << 2
    CLAP = 1 << 3


class SampleSet(Enum):
    NO_SAMPLE = 0
    NORMAL = 1
    SOFT = 2
    DRUM = 3


class SliderType(Enum):
    BEZIER = 'B'
    CATMUL = 'C'
    LINEAR = 'L'
    PERFECT = 'P'


@dataclass
class GeneralSettings:
    audio_filename: str = None
    audio_lead_in: int = 0
    audio_hash: str = None  # depricated
    preview_time: int = -1
    countdown: int = 1
    sample_set: str = "Normal"
    stack_leniency: float = 0.7
    mode: GameMode = 0
    letterbox_in_breaks: bool = False
    story_fire_in_front: bool = False  # depricated
    use_skin_sprites: bool = False
    always_show_playfield: bool = 0  # depricated
    overlay_position: str = "NoChange"
    skin_preference: str = None
    epilepsy_warning: bool = False
    countdown_offset: int = 0
    special_style: bool = False
    widescreen_storyboard: bool = False
    sample_match_playback: bool = False


@dataclass
class EditorSettings:
    bookmarks: List[int] = None
    distance_spacing: float = None
    beat_divisor: int = None
    grid_size: int = None
    timeline_zoom: float = None


@dataclass
class Metadata:
    title: str = None
    title_unicode: str = None
    artist: str = None
    artist_unicode: str = None
    creator: str = None
    version: str = None  # difficulty name
    source: str = None
    tags: List[str] = None
    beatmap_id: int = None
    beatmap_set_id: int = None


@dataclass
class Difficulty:
    hp_drain_rate: float = None
    circle_size: float = None
    overall_difficulty: float = None
    approach_rate: float = None
    slider_multiplier: float = None
    slider_tick_rate: float = None


@dataclass
class BaseEvent:
    start_time: int


@dataclass
class BackgroundEvent(BaseEvent):
    _id = 0
    filename: str
    x_offset: int = 0
    y_offset: int = 0


@dataclass
class VideoEvent(BaseEvent):
    _id = 1
    filename: str
    x_offset: int = 0
    y_offset: int = 0


@dataclass
class BreakEvent(BaseEvent):
    _id = 2
    end_time: int


@dataclass
class TimingPoint:
    time: int
    beat_length: float
    meter: int
    sample_set: HitSample
    uninherited: bool
    effects: int


@dataclass
class ComboColors:
    combo: List[Tuple[int, int, int]]
    slider_track_override: Tuple[int, int, int] = None
    slider_border: Tuple[int, int, int] = None


@dataclass
class HitSample:
    normal_set: int
    addition_set: int
    index: int
    volume: int
    filename: str


@dataclass
class BaseHitObject:
    x: int
    y: int
    time: int
    hit_sound: HitSound
    hit_sample: HitSample
    new_combo: bool
    combo_skips: int


@dataclass
class CircleObject(BaseHitObject):
    pass


@dataclass
class CurvePoint:
    x: int
    y: int


@dataclass
class SliderObject(BaseHitObject):
    curve_type: SliderType
    curve_points: List[CurvePoint]
    slides: int
    length: float
    edge_sounds: None
    edge_sets: None


@dataclass
class SpinnerObject(BaseHitObject):
    end_time: int


@dataclass
class ManiaHoldObject(BaseHitObject):
    end_time: int
