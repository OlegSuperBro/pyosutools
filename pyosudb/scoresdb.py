from dataclasses import dataclass
from typing import List, Union
import os
import io

from pyosudb import utils
from pyosudb.datatypes import BeatmapScores


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
            beatmaps.append(BeatmapScores.parse(self.score_db_file, version))

        return Scoresdb(version, count_beatmaps, beatmaps)


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
