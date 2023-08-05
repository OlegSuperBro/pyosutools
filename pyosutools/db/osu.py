from dataclasses import dataclass
from typing import List, ByteString
import datetime
import tempfile
import pickle
import io
import os

from pyosutools import utils
from pyosutools.datatypes import UserPermissions, BeatmapDB, Mod, GameMode, RankedStatus, ModStarRatingPair, TimingPoint


@dataclass
class Osudb:
    """
    Class representing osu!.db file

    Attributes
    ----
    game_version: int
        osu! version when this file created

    account_unlocked: bool
        Is account banned. False if banned, True otherwise

    unlock_datetime: datetime.datetime
        Time until account will be unbanned. Always 0 if account is not banned (account_unlocked=True)

    username: str
        Player username

    beatmaps: List
        List with all parsed beatmaps

    user_permissions: UserPermissions
        User permissions in chat. Check UserPermissions class for more info
    """
    game_version: int
    account_unlocked: bool  # false if account banned/locked
    unlock_datetime: datetime.datetime
    username: str

    beatmaps: List[BeatmapDB]

    user_permissions: UserPermissions

    @staticmethod
    def from_path(path: os.PathLike, skip_beatmaps: bool = False):
        with open(path, "rb") as f:
            return Osudb.from_file(f, skip_beatmaps)

    @staticmethod
    def from_file(file: io.BufferedReader, skip_beatmaps: bool = False):
        return Osudb.from_data(file.read(), skip_beatmaps)

    @staticmethod
    def from_data(data: ByteString, skip_beatmaps: bool = False):
        return _Parser(data).parse(skip_beatmaps)

    def save_cache_beatmaps(self, cache_path: os.PathLike = tempfile.mkstemp(prefix="osudb_parser", suffix=".json")):
        with open(cache_path, "wb") as f:
            pickle.dump(self.beatmaps, f)

    def load_cache_beatmaps(self, cache_path: os.PathLike = tempfile.mkstemp(prefix="osudb_parser", suffix=".json")):
        with open(cache_path, "rb") as f:
            self.beatmaps = pickle.load(f)


class _Parser:
    def __init__(self, data) -> None:
        self.data_io = io.BytesIO(data)

    def parse(self, skip_beatmaps: bool = False) -> Osudb:
        game_version = utils.read_uint(self.data_io)
        utils.read_uint(self.data_io)  # ignoring folder count cuz we don't need it
        account_unlocked = utils.read_bool(self.data_io)
        unlock_datetime = utils.read_datetime(self.data_io)
        username = utils.read_string(self.data_io)

        count_beatmaps = utils.read_uint(self.data_io)

        if skip_beatmaps:
            for _ in range(count_beatmaps):
                self.parse_beatmap(game_version)
        else:
            beatmaps = [self.parse_beatmap(game_version) for _ in range(count_beatmaps)]

        user_permissions = UserPermissions(utils.read_uint(self.data_io))

        return Osudb(game_version, account_unlocked, unlock_datetime, username, beatmaps, user_permissions)

    def parse_beatmap(self, game_ver: int = 0):
        """
        Parse beatmap

        Args
        ----
        game_ver: int
            Version of game

        Returns
        ----
        Beatmap
            Parsed beatmap instance
        """
        if game_ver < 20191106:
            utils.read_uint(self.data_io)  # ignore size
        artist = utils.read_string(self.data_io)
        artist_unicode = utils.read_string(self.data_io)
        title = utils.read_string(self.data_io)

        title_unicode = utils.read_string(self.data_io)
        creator = utils.read_string(self.data_io)
        difficulty = utils.read_string(self.data_io)
        audio_file = utils.read_string(self.data_io)
        md5_hash = utils.read_string(self.data_io)
        osu_file = utils.read_string(self.data_io)

        ranked_status = RankedStatus(utils.read_ubyte(self.data_io))
        count_hitcircles = utils.read_ushort(self.data_io)
        count_sliders = utils.read_ushort(self.data_io)
        count_spiners = utils.read_ushort(self.data_io)

        last_modification = utils.read_datetime(self.data_io)

        if game_ver < 20140609:
            ar = utils.read_ubyte(self.data_io)
            cs = utils.read_ubyte(self.data_io)
            hp = utils.read_ubyte(self.data_io)
            od = utils.read_ubyte(self.data_io)
        else:
            ar = utils.read_float(self.data_io)
            cs = utils.read_float(self.data_io)
            hp = utils.read_float(self.data_io)
            od = utils.read_float(self.data_io)

        slider_velocity = utils.read_double(self.data_io)

        std_pairs = []
        taiko_pairs = []
        ctb_pairs = []
        mania_pairs = []
        if game_ver >= 20140609:
            for _ in range(utils.read_uint(self.data_io)):
                tmp = utils.read_int_double(self.data_io)
                std_pairs.append(ModStarRatingPair(Mod(tmp[0]), tmp[1]))

            for _ in range(utils.read_uint(self.data_io)):
                tmp = utils.read_int_double(self.data_io)
                taiko_pairs.append(ModStarRatingPair(Mod(tmp[0]), tmp[1]))

            for _ in range(utils.read_uint(self.data_io)):
                tmp = utils.read_int_double(self.data_io)
                ctb_pairs.append(ModStarRatingPair(Mod(tmp[0]), tmp[1]))

            for _ in range(utils.read_uint(self.data_io)):
                tmp = utils.read_int_double(self.data_io)
                mania_pairs.append(ModStarRatingPair(Mod(tmp[0]), tmp[1]))

        drain_time = utils.read_uint(self.data_io)
        total_time = utils.read_uint(self.data_io)
        preview_time = utils.read_uint(self.data_io)

        timing_points = [
            TimingPoint(*utils.read_timing_point(self.data_io))
            for _ in range(utils.read_uint(self.data_io))
        ]

        difficulty_id = utils.read_uint(self.data_io)
        beatmap_id = utils.read_uint(self.data_io)
        thread_id = utils.read_uint(self.data_io)

        std_grade = utils.read_ubyte(self.data_io)
        taiko_grade = utils.read_ubyte(self.data_io)
        ctb_grade = utils.read_ubyte(self.data_io)
        mania_grade = utils.read_ubyte(self.data_io)

        local_offset = utils.read_ushort(self.data_io)
        stack_laniency = utils.read_float(self.data_io)

        gameplay_mode = GameMode(utils.read_ubyte(self.data_io))

        song_source = utils.read_string(self.data_io)
        song_tags = utils.read_string(self.data_io)

        online_offset = utils.read_ushort(self.data_io)

        title_font = utils.read_string(self.data_io)

        unplayed = utils.read_bool(self.data_io)
        last_played = utils.read_datetime(self.data_io)

        is_osz2 = utils.read_bool(self.data_io)
        folder_name = utils.read_string(self.data_io)
        last_checked = utils.read_datetime(self.data_io)

        ignore_sound = utils.read_bool(self.data_io)
        ignore_skin = utils.read_bool(self.data_io)
        disable_storyboard = utils.read_bool(self.data_io)
        disable_video = utils.read_bool(self.data_io)

        visual_override = utils.read_bool(self.data_io)

        if game_ver < 20140609:
            utils.read_uint(self.data_io)  # osu! wiki page literally says it's unknown and present if game version less than 20140609

        utils.read_uint(self.data_io)  # ignore second modification time

        mania_scroll_speed = utils.read_ubyte(self.data_io)

        return BeatmapDB(artist, artist_unicode, title, title_unicode, creator, difficulty, audio_file, md5_hash, osu_file, ranked_status, count_hitcircles, count_sliders,
                         count_spiners, last_modification, ar, cs, hp, od, slider_velocity, std_pairs, taiko_pairs, ctb_pairs, mania_pairs, drain_time, total_time, preview_time,
                         timing_points, difficulty_id, beatmap_id, thread_id, std_grade, taiko_grade, ctb_grade, mania_grade, local_offset, stack_laniency, gameplay_mode, song_source,
                         song_tags, online_offset, title_font, unplayed, last_played, is_osz2, folder_name, last_checked, ignore_sound, ignore_skin, disable_storyboard, disable_video,
                         visual_override, mania_scroll_speed)
