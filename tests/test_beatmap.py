import glob
from pathlib import Path

from pyosutools.beatmap.beatmap import Beatmap

RESOURCES_PATH = Path(r"tests\resources\beatmaps")


def test_v3():
    for file in glob.iglob(str(RESOURCES_PATH / "v3" / "*.osu")):
        assert Beatmap.from_path(file) is not None


def test_v5():
    for file in glob.iglob(str(RESOURCES_PATH / "v5" / "*.osu")):
        assert Beatmap.from_path(file) is not None


def test_v6():
    for file in glob.iglob(str(RESOURCES_PATH / "v6" / "*.osu")):
        assert Beatmap.from_path(file) is not None


def test_v7():
    for file in glob.iglob(str(RESOURCES_PATH / "v7" / "*.osu")):
        assert Beatmap.from_path(file) is not None


def test_v8():
    for file in glob.iglob(str(RESOURCES_PATH / "v8" / "*.osu")):
        assert Beatmap.from_path(file) is not None


def test_v9():
    for file in glob.iglob(str(RESOURCES_PATH / "v9" / "*.osu")):
        assert Beatmap.from_path(file) is not None


def test_v10():
    for file in glob.iglob(str(RESOURCES_PATH / "v10" / "*.osu")):
        assert Beatmap.from_path(file) is not None


def test_v11():
    for file in glob.iglob(str(RESOURCES_PATH / "v11" / "*.osu")):
        assert Beatmap.from_path(file) is not None


def test_v12():
    for file in glob.iglob(str(RESOURCES_PATH / "v12" / "*.osu")):
        assert Beatmap.from_path(file) is not None


def test_v13():
    for file in glob.iglob(str(RESOURCES_PATH / "v13" / "*.osu")):
        assert Beatmap.from_path(file) is not None


def test_v14():
    for file in glob.iglob(str(RESOURCES_PATH / "v14" / "*.osu")):
        assert Beatmap.from_path(file) is not None
