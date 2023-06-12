from enum import Enum, IntFlag
from dataclasses import dataclass
from typing import Optional, List
import io
import datetime
import pickle

from pyosudb import utils


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
    size: Optional[int]  # only present if osu! version is less than 20191106
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

    unknown: Optional[int]  # osu! wiki page literally says it's unknown and present if game version less than 20140609

    last_modification2: datetime.datetime  # ?

    mania_scroll_speed: int

    @staticmethod
    def parse(buffer: io.BytesIO, game_ver: int = 0):
        """
        Parse beatmap from file

        Args
        ----
        buffer: io.BytesIO
            Opened file
        game_ver: int
            Version of game

        Returns
        ----
        Beatmap
            Parsed beatmap
        """
        size = None
        if game_ver < 20191106:
            size = utils.read_uint(buffer)
        artist = utils.read_string(buffer)
        artist_unicode = utils.read_string(buffer)
        title = utils.read_string(buffer)

        title_unicode = utils.read_string(buffer)
        creator = utils.read_string(buffer)
        difficulty = utils.read_string(buffer)
        audio_file = utils.read_string(buffer)
        md5_hash = utils.read_string(buffer)
        osu_file = utils.read_string(buffer)

        ranked_status = RankedStatus(utils.read_ubyte(buffer))
        count_hitcircles = utils.read_ushort(buffer)
        count_sliders = utils.read_ushort(buffer)
        count_spiners = utils.read_ushort(buffer)

        last_modification = utils.read_datetime(buffer)

        if game_ver < 20140609:
            ar = utils.read_ubyte(buffer)
            cs = utils.read_ubyte(buffer)
            hp = utils.read_ubyte(buffer)
            od = utils.read_ubyte(buffer)
        else:
            ar = utils.read_float(buffer)
            cs = utils.read_float(buffer)
            hp = utils.read_float(buffer)
            od = utils.read_float(buffer)

        slider_velocity = utils.read_double(buffer)

        std_pairs = []
        taiko_pairs = []
        ctb_pairs = []
        mania_pairs = []
        if game_ver >= 20140609:
            for _ in range(utils.read_uint(buffer)):
                tmp = utils.read_int_double(buffer)
                std_pairs.append(ModStarRatingPair(Mod(tmp[0]), tmp[1]))

            for _ in range(utils.read_uint(buffer)):
                tmp = utils.read_int_double(buffer)
                taiko_pairs.append(ModStarRatingPair(Mod(tmp[0]), tmp[1]))

            for _ in range(utils.read_uint(buffer)):
                tmp = utils.read_int_double(buffer)
                ctb_pairs.append(ModStarRatingPair(Mod(tmp[0]), tmp[1]))

            for _ in range(utils.read_uint(buffer)):
                tmp = utils.read_int_double(buffer)
                mania_pairs.append(ModStarRatingPair(Mod(tmp[0]), tmp[1]))

        drain_time = utils.read_uint(buffer)
        total_time = utils.read_uint(buffer)
        preview_time = utils.read_uint(buffer)

        timing_points = []
        for _ in range(utils.read_uint(buffer)):
            timing_points.append(TimingPoint(*utils.read_timing_point(buffer)))

        difficulty_id = utils.read_uint(buffer)
        beatmap_id = utils.read_uint(buffer)
        thread_id = utils.read_uint(buffer)

        std_grade = utils.read_ubyte(buffer)
        taiko_grade = utils.read_ubyte(buffer)
        ctb_grade = utils.read_ubyte(buffer)
        mania_grade = utils.read_ubyte(buffer)

        local_offset = utils.read_ushort(buffer)
        stack_laniency = utils.read_float(buffer)

        gameplay_mode = GameMode(utils.read_ubyte(buffer))

        song_source = utils.read_string(buffer)
        song_tags = utils.read_string(buffer)

        online_offset = utils.read_ushort(buffer)

        title_font = utils.read_string(buffer)

        unplayed = utils.read_bool(buffer)
        last_played = utils.read_datetime(buffer)

        is_osz2 = utils.read_bool(buffer)
        folder_name = utils.read_string(buffer)
        last_checked = utils.read_datetime(buffer)

        ignore_sound = utils.read_bool(buffer)
        ignore_skin = utils.read_bool(buffer)
        disable_storyboard = utils.read_bool(buffer)
        disable_video = utils.read_bool(buffer)

        visual_override = utils.read_bool(buffer)

        unknown = None
        if game_ver < 20140609:
            unknown = utils.read_uint(buffer)  # osu! wiki page literally says it's unknown and present if game version less than 20140609

        last_modification_time = utils.read_uint(buffer)

        mania_scroll_speed = utils.read_ubyte(buffer)

        return Beatmap(size, artist, artist_unicode, title, title_unicode, creator, difficulty, audio_file, md5_hash, osu_file, ranked_status, count_hitcircles, count_sliders,
                       count_spiners, last_modification, ar, cs, hp, od, slider_velocity, std_pairs, taiko_pairs, ctb_pairs, mania_pairs, drain_time, total_time, preview_time,
                       timing_points, difficulty_id, beatmap_id, thread_id, std_grade, taiko_grade, ctb_grade, mania_grade, local_offset, stack_laniency, gameplay_mode, song_source,
                       song_tags, online_offset, title_font, unplayed, last_played, is_osz2, folder_name, last_checked, ignore_sound, ignore_skin, disable_storyboard, disable_video,
                       visual_override, unknown, last_modification_time, mania_scroll_speed)

    @staticmethod
    def from_sql(*args):
        # TODO: rewrite func cuz this one is kinda unsave
        """
        Get beatmap from sql row

        Returns
        ----
        Beatmap
            osu! beatmap
        """
        new_args = []
        for arg in args:
            if arg is None:
                new_args.append(arg)
                continue

            if type(arg) == str and (arg[:2] == "b\'" or arg[:2] == "b\""):
                new_args.append(pickle.loads(bytearray(eval(arg))))
                continue
            new_args.append(arg)

        return Beatmap(*new_args)


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

    def parse(buffer: io.BytesIO, game_ver: int = 0):
        """
        Parse score from file

        Args
        ----
        buffer: io.BytesIO
            Opened file
        game_ver: int
            Version of game

        Returns
        ----
        Beatmap
            Parsed score
        """
        gamemode = GameMode(utils.read_ubyte(buffer))
        score_version = utils.read_uint(buffer)
        beatmap_hash = utils.read_string(buffer)
        username = utils.read_string(buffer)
        replay_hash = utils.read_string(buffer)

        count_300 = utils.read_ushort(buffer)
        count_100 = utils.read_ushort(buffer)
        count_50 = utils.read_ushort(buffer)
        count_geki = utils.read_ushort(buffer)
        count_katu = utils.read_ushort(buffer)
        count_miss = utils.read_ushort(buffer)

        total_score = utils.read_uint(buffer)
        max_combo = utils.read_ushort(buffer)
        perfect_combo = utils.read_bool(buffer)

        mods = Mod(utils.read_uint(buffer))

        utils.read_string(buffer)  # this one always should be empty for some reason, skip it
        timestamp = utils.read_datetime(buffer)
        utils.read_uint(buffer)  # always should be -1, skip it
        online_score_id = utils.read_ulong(buffer)

        additional_info = None
        # if target practice in mods
        if Mod(1 << 23) in mods:
            additional_info = utils.read_double(buffer)

        return Score(gamemode, score_version, beatmap_hash, username, replay_hash,
                     count_300, count_100, count_50, count_geki, count_katu, count_miss,
                     total_score, max_combo, perfect_combo, timestamp, online_score_id, additional_info)


@dataclass
class BeatmapScores:
    """
    List of scores on beatmap
    """
    beatmap_hash: str
    count_scores: int
    scores: List[Score]

    @staticmethod
    def parse(buffer: io.BytesIO, game_ver: int = 0):
        beatmap_hash = utils.read_string(buffer)
        count_scores = utils.read_uint(buffer)
        scores = []
        for _ in range(count_scores):
            scores.append(Score.parse(buffer, game_ver))

        return BeatmapScores(beatmap_hash, count_scores, scores)


@dataclass
class Collection:
    """
    osu! collection with beatmaps
    """
    name: str
    count_beatmaps: int
    beatmaps_hash: List[str]

    @staticmethod
    def parse(buffer: io.BytesIO, game_ver: int = 0):
        name = utils.read_string(buffer)
        count_beatmaps = utils.read_uint(buffer)
        beatmaps_hash = []

        for _ in range(count_beatmaps):
            beatmaps_hash.append(utils.read_string(buffer))

        return Collection(name, count_beatmaps, beatmaps_hash)
