from dataclasses import dataclass
from typing import List, ByteString
import os
import io

from pyosutools.datatypes import BeatmapScores, Score
from pyosutools.datatypes import GameMode, Mod
from pyosutools import utils


@dataclass
class Scoresdb:
    """
    Class representing scores.db file

    Attributes
    ----
    version: int
        osu! version when this file created

    count_beatmaps_scores: int
        Amount of beatmaps scores in .db file

    beatmaps_scores: List[BeatmapScores]
        List of scores on beatmaps represented by "BeatmapScores" class
    """
    version: int
    count_beatmaps_scores: int
    beatmaps_scores: List[BeatmapScores]

    @staticmethod
    def from_path(path: os.PathLike):
        with open(path, "rb") as f:
            return Scoresdb.from_file(f)

    @staticmethod
    def from_file(file: io.BufferedReader):
        return Scoresdb.from_data(file.read())

    @staticmethod
    def from_data(data: ByteString):
        return _Parser(data).parse()


class _Parser:
    def __init__(self, data) -> None:
        self.data_io = io.BytesIO(data)

    def parse(self) -> Scoresdb:
        version = utils.read_uint(self.data_io)
        count_beatmaps = utils.read_uint(self.data_io)
        scores = [self.parse_beatmap_scores(version) for _ in range(count_beatmaps)]

        return Scoresdb(version, count_beatmaps, scores)

    def parse_score(self, game_ver: int = 0):
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
        gamemode = GameMode(utils.read_ubyte(self.data_io))
        score_version = utils.read_uint(self.data_io)
        beatmap_hash = utils.read_string(self.data_io)
        username = utils.read_string(self.data_io)
        replay_hash = utils.read_string(self.data_io)

        count_300 = utils.read_ushort(self.data_io)
        count_100 = utils.read_ushort(self.data_io)
        count_50 = utils.read_ushort(self.data_io)
        count_geki = utils.read_ushort(self.data_io)
        count_katu = utils.read_ushort(self.data_io)
        count_miss = utils.read_ushort(self.data_io)

        total_score = utils.read_uint(self.data_io)
        max_combo = utils.read_ushort(self.data_io)
        perfect_combo = utils.read_bool(self.data_io)

        mods = Mod(utils.read_uint(self.data_io))

        utils.read_string(self.data_io)  # this one always should be empty for some reason, skip it
        timestamp = utils.read_datetime(self.data_io)
        utils.read_uint(self.data_io)  # always should be -1, skip it
        online_score_id = utils.read_ulong(self.data_io)

        additional_info = None
        # if target practice in mods
        if Mod(1 << 23) in mods:
            additional_info = utils.read_double(self.data_io)

        return Score(gamemode, score_version, beatmap_hash, username, replay_hash,
                     count_300, count_100, count_50, count_geki, count_katu, count_miss,
                     total_score, max_combo, perfect_combo, timestamp, online_score_id, additional_info)

    def parse_beatmap_scores(self, game_ver: int = 0):
        beatmap_hash = utils.read_string(self.data_io)
        count_scores = utils.read_uint(self.data_io)
        scores = [self.parse_score(game_ver) for _ in range(count_scores)]
        return BeatmapScores(beatmap_hash, count_scores, scores)
