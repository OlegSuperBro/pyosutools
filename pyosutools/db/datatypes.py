from aenum import Enum, IntFlag
from dataclasses import dataclass
from typing import Optional, List
import datetime

from pyosutools.datatypes import Mod, GameMode


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
    osu! user permission in chat
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
    Timing point in osu! beatmap
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
class Beatmap:
    """
    osu! beatmap
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

    timing_points: List[TimingPoint]

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


@dataclass
class Score:
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
    scores: List[Score]


@dataclass
class Collection:
    """
    osu! collection with beatmaps
    """
    name: str
    count_beatmaps: int
    beatmaps_hash: List[str]
