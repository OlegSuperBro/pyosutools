from dataclasses import dataclass
from typing import List, Union
import os
import io

from pyosutools import utils
from pyosutools.db.datatypes import Collection


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


class _Parser:
    def __init__(self, collection_db_file) -> None:
        self.collection_db_file = collection_db_file
        self.offset = 0

    def parse(self) -> Collectiondb:
        version = utils.read_uint(self.collection_db_file)
        count_collections = utils.read_uint(self.collection_db_file)
        collections = []
        for _ in range(count_collections):
            collections.append(self.parse_collection(version))

        return Collectiondb(version, count_collections, collections)

    def parse_collection(self, game_ver: int = 0):
        name = utils.read_string(self.collection_db_file)
        count_beatmaps = utils.read_uint(self.collection_db_file)
        beatmaps_hash = []

        for _ in range(count_beatmaps):
            beatmaps_hash.append(utils.read_string(self.collection_db_file))

        return Collection(name, count_beatmaps, beatmaps_hash)


def parse_collectiondb(collectiondb_file: Union[str, os.PathLike, io.BytesIO]) -> Collectiondb:
    """
    Parse collection.db file

    Args
    ----
    collectiondb_file: str | os.PathLike | io.BytesIO
        Path or opened file

    Returns
    ----
    Collectiondb
        instance of Collectiondb class
    """
    if not isinstance(collectiondb_file, io.BytesIO):
        collectiondb_file = open(collectiondb_file, "rb")

    return _Parser(collectiondb_file).parse()
