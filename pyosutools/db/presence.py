from dataclasses import dataclass
from typing import List

from pyosutools import utils


class _Parser:
    def __init__(self, db_file) -> None:
        self.db_file = db_file

    def parse(self):
        return None

@dataclass
class Presencedb:
    """
    DO NOT USE IT FOR NOW!

    I'm currentry searching info about presence.db file, so this don't works.
    """
    version: int
    count: int
    values: List
