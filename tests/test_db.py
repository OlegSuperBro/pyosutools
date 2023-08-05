from pathlib import Path

from pyosutools.db.osu import Osudb
from pyosutools.db.collection import Collectiondb
from pyosutools.db.scores import Scoresdb
from pyosutools.db.presence import Presencedb

RESOURCES_PATH = Path(r"tests\resources\db_files")


def test_osudb():
    db = Osudb.from_path(RESOURCES_PATH / "osu!.db")
    assert db is not None
    assert db.beatmaps != []


def test_collectiondb():
    db = Collectiondb.from_path(RESOURCES_PATH / "collection.db")
    assert db is not None
    assert db.collections != []


def test_scoresdb():
    db = Scoresdb.from_path(RESOURCES_PATH / "scores.db")
    assert db is not None
    assert db.beatmaps_scores != []


# def test_presencedb():
#     assert Osudb.from_path(RESOURCES_PATH / "osu.db")
