from dataclasses import dataclass
from typing import List, ByteString
import os
import io

from pyosutools import utils
from pyosutools.datatypes import Collection


@dataclass
class Collectiondb:
    """
    Class representing collection.db file

    Attributes
    ----
    version: int
        osu! version when this file created

    count_collections: int
        Amount of collections in .db file

    collections: List[Collection]
        List of collections represented by "Collection" class
    """
    version: int
    count_collections: int
    collections: List[Collection]

    @staticmethod
    def from_path(path: os.PathLike):
        with open(path, "rb") as f:
            return Collectiondb.from_file(f)

    @staticmethod
    def from_file(file: io.BufferedReader):
        return Collectiondb.from_data(file.read())

    @staticmethod
    def from_data(data: ByteString):
        return _Parser(data).parse()


class _Parser:
    def __init__(self, data) -> None:
        self.data_io = io.BytesIO(data)
        self.offset = 0

    def parse(self) -> Collectiondb:
        version = utils.read_uint(self.data_io)
        count_collections = utils.read_uint(self.data_io)
        collections = [
            self.parse_collection(version) for _ in range(count_collections)
        ]
        return Collectiondb(version, count_collections, collections)

    def parse_collection(self, game_ver: int = 0):
        name = utils.read_string(self.data_io)
        count_beatmaps = utils.read_uint(self.data_io)

        beatmaps_hash = [
            utils.read_string(self.data_io)
            for _ in range(count_beatmaps)
        ]

        return Collection(name, count_beatmaps, beatmaps_hash)
