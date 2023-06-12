from pathlib import Path
from datetime import datetime

import pyosudb
from pyosudb.datatypes import UserPermissions

RES = Path(__file__).parent / "resources"


def test_parsing_osudb():
    db = pyosudb.parse_osudb(RES / "osu!.db", RES / "tmp_osudb.sql")
    assert db.game_version == 20230319
    assert db.folder_count == 2736
    assert db.account_unlocked is True
    assert db.unlock_datetime == datetime.min
    assert db.username == "OlegSuperBro"
    assert db.count_beatmaps == 12020
    assert len(db.beatmaps()) == db.count_beatmaps
    assert db.user_permissions == UserPermissions.NORMAL


def test_parsing_osudb_with_sql():
    db = pyosudb.parse_osudb(RES / "osu!.db", RES / "beatmaps.sql", skip_beatmaps=True)
    assert db.game_version == 20230319
    assert db.folder_count == 2736
    assert db.account_unlocked is True
    assert db.unlock_datetime == datetime.min
    assert db.username == "OlegSuperBro"
    assert db.count_beatmaps == 12020
    assert len(db.beatmaps()) == db.count_beatmaps
    assert db.user_permissions == UserPermissions.NORMAL
