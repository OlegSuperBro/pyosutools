from dataclasses import dataclass
from typing import List
import os
import io

from pyosudb import utils
from pyosudb.datatypes import Collection


@dataclass
class Collectiondb:
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
            collections.append(Collection.parse(self.collection_db_file, version))

        return Collectiondb(version, count_collections, collections)


def parse_collectiondb(osudb_file: str | os.PathLike | io.BytesIO) -> Collectiondb:
    if not isinstance(osudb_file, io.BytesIO):
        osudb_file = open(osudb_file, "rb")

    return _Parser(osudb_file).parse()
