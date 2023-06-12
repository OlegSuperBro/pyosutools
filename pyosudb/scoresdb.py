from dataclasses import dataclass
from typing import List, Union
import os
import io

from pyosudb import utils
from pyosudb.datatypes import BeatmapScores


@dataclass
class Scoresdb:
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


def parse_scoresdb(osudb_file: Union[str, os.PathLike, io.BytesIO]) -> Scoresdb:
    if not isinstance(osudb_file, io.BytesIO):
        osudb_file = open(osudb_file, "rb")

    return _Parser(osudb_file).parse()
