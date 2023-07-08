from dataclasses import dataclass
from typing import List, Union
import os
import io

from pyosutools.db.datatypes import BeatmapScores, Score
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


class _Parser:
    def __init__(self, score_db_file) -> None:
        self.score_db_file = score_db_file
        self.offset = 0

    def parse(self) -> Scoresdb:
        version = utils.read_uint(self.score_db_file)
        count_beatmaps = utils.read_uint(self.score_db_file)
        beatmaps = []
        for _ in range(count_beatmaps):
            beatmaps.append(self.parse_beatmap_scores(version))

        return Scoresdb(version, count_beatmaps, beatmaps)

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
        gamemode = GameMode(utils.read_ubyte(self.score_db_file))
        score_version = utils.read_uint(self.score_db_file)
        beatmap_hash = utils.read_string(self.score_db_file)
        username = utils.read_string(self.score_db_file)
        replay_hash = utils.read_string(self.score_db_file)

        count_300 = utils.read_ushort(self.score_db_file)
        count_100 = utils.read_ushort(self.score_db_file)
        count_50 = utils.read_ushort(self.score_db_file)
        count_geki = utils.read_ushort(self.score_db_file)
        count_katu = utils.read_ushort(self.score_db_file)
        count_miss = utils.read_ushort(self.score_db_file)

        total_score = utils.read_uint(self.score_db_file)
        max_combo = utils.read_ushort(self.score_db_file)
        perfect_combo = utils.read_bool(self.score_db_file)

        mods = Mod(utils.read_uint(self.score_db_file))

        utils.read_string(self.score_db_file)  # this one always should be empty for some reason, skip it
        timestamp = utils.read_datetime(self.score_db_file)
        utils.read_uint(self.score_db_file)  # always should be -1, skip it
        online_score_id = utils.read_ulong(self.score_db_file)

        additional_info = None
        # if target practice in mods
        if Mod(1 << 23) in mods:
            additional_info = utils.read_double(self.score_db_file)

        return Score(gamemode, score_version, beatmap_hash, username, replay_hash,
                     count_300, count_100, count_50, count_geki, count_katu, count_miss,
                     total_score, max_combo, perfect_combo, timestamp, online_score_id, additional_info)

    def parse_beatmap_scores(self, game_ver: int = 0):
        beatmap_hash = utils.read_string(self.score_db_file)
        count_scores = utils.read_uint(self.score_db_file)
        scores = []
        for _ in range(count_scores):
            scores.append(self.parse_score(game_ver))

        return BeatmapScores(beatmap_hash, count_scores, scores)


def parse_scoresdb(scoresdb_file: Union[str, os.PathLike, io.BytesIO]) -> Scoresdb:
    """
    Parse scores.db file

    Args
    ----
    scoresdb_file: str | os.PathLike | io.BytesIO
        Path or opened file

    Returns
    ----
    scoresdb
        instance of scoresdb class
    """
    if not isinstance(scoresdb_file, io.BytesIO):
        scoresdb_file = open(scoresdb_file, "rb")

    return _Parser(scoresdb_file).parse()
