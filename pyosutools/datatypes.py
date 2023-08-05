from __future__ import annotations
from aenum import Enum, IntFlag
from dataclasses import dataclass
from typing import List, Tuple, Optional
import datetime


# ---------UNIVERSAL STUFF--------- #
class GameMode(Enum):
    """
    osu! gamemodes
    """
    STD = 0
    TAIKO = 1
    CTB = 2
    MANIA = 3


class Mod(IntFlag):
    """
    osu! mods or their combination
    """
    NM = 0
    NF = 1 << 0
    EZ = 1 << 1
    TD = 1 << 2
    HD = 1 << 3
    HR = 1 << 4
    SD = 1 << 5
    DT = 1 << 6
    RX = 1 << 7
    HT = 1 << 8
    NC = 1 << 9
    FL = 1 << 10
    AT = 1 << 11
    SO = 1 << 12
    AP = 1 << 13
    PF = 1 << 14
    K4 = 1 << 15
    K5 = 1 << 16
    K6 = 1 << 17
    K7 = 1 << 18
    K8 = 1 << 19
    FD = 1 << 20
    RD = 1 << 21
    CN = 1 << 22
    TP = 1 << 23
    K9 = 1 << 24
    CO = 1 << 25
    K1 = 1 << 26
    K3 = 1 << 27
    K2 = 1 << 28
    V2 = 1 << 29
    MR = 1 << 30


# ----------BEATMAP STUFF---------- #
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
class BeatmapTimingPoint:
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


# ---------DATABASES STUFF--------- #

class Grade(Enum):
    """
    osu! grades on scores
    """
    SS_silver = 0
    S_silver = 1
    SS = 2
    S = 3
    A = 4
    B = 5
    C = 6
    D = 7
    Unplayed = 9


# osu!.db
class RankedStatus(Enum):
    """
    osu! beatmap statuses
    """
    UNKNOWN = 0
    UNSUBMITTED = 1
    PENDING = 2  # also wip and graveyard
    UNUSED = 3  # ???
    RANKED = 4
    APPROVED = 5
    QUALIFIED = 6
    LOVED = 7


class UserPermissions(IntFlag):
    """
    osu! user permission
    """
    UNKNOWN = 0
    NORMAL = 1
    MODERATOR = 1 << 1
    SUPPORTER = 1 << 2
    FRIEND = 1 << 3
    PEPPY = 1 << 4
    WORLD_CUP_STAFF = 1 << 5


@dataclass
class TimingPoint:
    """
    Timing point in BeatmapDB
    """
    bpm: float
    offset: float
    inherited: bool


@dataclass
class ModStarRatingPair:
    """
    Pairs for beatmaps with mods combination and their star rating with those mods
    """
    mod: Mod
    star_rating: float


@dataclass
class BeatmapDB:
    """
    osu! beatmap used in osu!.db file
    """
    artist: str
    artist_unicode: str
    title: str
    title_unicode: str
    mapper: str
    difficulty: str
    audio_file: str
    md5_hash: str
    osu_file: str

    ranked_status: RankedStatus
    count_hitcircles: int
    count_sliders: int
    count_spinners: int
    last_modification: datetime.datetime

    ar: int
    cs: int
    hp: int
    od: int
    slider_velocity: float

    std_pairs: List[ModStarRatingPair]
    taiko_pairs: List[ModStarRatingPair]
    ctb_pairs: List[ModStarRatingPair]
    mania_pairs: List[ModStarRatingPair]

    drain_time: int
    total_time: int
    preview_time: int

    timing_points: List[BeatmapTimingPoint]

    difficulty_id: int
    beatmap_id: int
    thread_id: int

    std_grade: int
    taiko_grade: int
    ctb_grade: int
    mania_grade: int

    local_offset: int
    stack_leniency: int

    gameplay_mode: GameMode

    song_source: str
    song_tags: str

    online_offset: int

    title_font: str

    unplayed: bool
    last_played: datetime.datetime

    is_osz2: bool
    folder_name: str
    last_checked: datetime.datetime

    ignore_sound: bool
    ignore_skin: bool
    disable_storyboard: bool
    disable_video: bool

    visual_override: bool

    mania_scroll_speed: int


# scores.db
@dataclass
class ScoreDB:
    """
    osu! score
    """
    gamemode: GameMode
    score_version: int
    beatmap_hash: str
    username: str
    replay_hash: str

    count_300: int
    count_100: int
    count_50: int
    count_geki: int
    count_katu: int
    count_miss: int

    total_score: int
    max_combo: int
    perfect_combo: bool

    mods: Mod

    timestamp: datetime.datetime
    online_score_id: int
    additional_info: Optional[float] = 0


@dataclass
class BeatmapScores:
    """
    List of scores on beatmap
    """
    beatmap_hash: str
    count_scores: int
    scores: List[ScoreDB]


# collection.db
@dataclass
class Collection:
    """
    osu! collection with beatmaps
    """
    name: str
    count_beatmaps: int
    beatmaps_hash: List[str]
