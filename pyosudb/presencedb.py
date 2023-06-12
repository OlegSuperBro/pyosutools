from dataclasses import dataclass
from typing import List

from pyosudb import utils


class _PresencedbParser:
    def __init__(self, osu_db_file) -> None:
        self.osu_db_file = osu_db_file
        self.offset = 0

    def parse(self):
        version = utils.read_uint(self.osu_db_file)
        count = utils.read_uint(self.osu_db_file)
        # 2 ?
        gamemode = utils.read_ubyte(self.osu_db_file)  # ?
        # ?
        rank = utils.read_uint(self.osu_db_file)
        # return Presencedb(version, count)


@dataclass
class Presencedb:
    version: int
    count: int
    values: List


if __name__ == "__main__":
    a = _PresencedbParser(open(r"C:\Users\olegrakov\Desktop\presence.db", "rb"))
    a.parse()
