from dataclasses import dataclass
import datetime
import tempfile
import sqlite3
import pickle
import io
import os

from pyosudb import utils
from pyosudb.datatypes import Beatmap, UserPermissions


@dataclass
class Osudb:
    game_version: int
    folder_count: int
    account_unlocked: bool  # false if account banned/locked
    unlock_datetime: datetime.datetime
    username: str
    count_beatmaps: int

    sql_beatmaps_db: sqlite3.Connection

    user_permissions: UserPermissions

    # can't be saved because osu.db can be big and we don't need 20k objects with maps in our ram
    def beatmaps(self):
        cursor = self.sql_beatmaps_db.cursor()
        return [Beatmap.from_sql(*beatmap) for beatmap in cursor.execute("SELECT * FROM 'beatmaps' ")]

    def get_beatmap_from_hash(self, hash):
        cursor = self.sql_beatmaps_db.cursor()
        return Beatmap.from_sql(cursor.execute(f"SELECT * FROM 'beatmaps' WHERE md5_hash='{hash}'")[0])

    def beatmaps_execute_sql(self, command):
        cursor = self.sql_beatmaps_db.cursor()
        return cursor.execute(command)


class _Parser:
    def __init__(self, osu_db_file) -> None:
        self.osu_db_file = osu_db_file
        self.offset = 0

    def generate_sql_db(self):
        cursor = self.beatmaps_db.cursor()
        cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='beatmaps'")
        if cursor.fetchone()[0] == 1:
            self.beatmaps_db.execute("DROP TABLE beatmaps")
        self.beatmaps_db.execute("""CREATE TABLE beatmaps (
                            size INTEGER,
                            artist TEXT,
                            artist_unicode TEXT,
                            title TEXT,
                            title_unicode TEXT,
                            mapper TEXT,
                            difficulty TEXT,
                            audio_file TEXT,
                            md5_hash TEXT,
                            osu_file TEXT,
                            ranked_status TEXT,
                            count_hitcircles INTEGER,
                            count_sliders INTEGER,
                            count_spinners INTEGER,
                            last_modification TEXT,
                            ar NUMERIC,
                            cs NUMERIC,
                            hp NUMERIC,
                            od NUMERIC,
                            slider_velocity NUMERIC,
                            std_pairs TEXT,
                            taiko_pairs TEXT,
                            ctb_pairs TEXT,
                            mania_pairs TEXT,
                            drain_time INTEGER,
                            total_time INTEGER,
                            preview_time INTEGER,
                            timing_points TEXT,
                            difficulty_id INTEGER,
                            beatmap_id INTEGER,
                            thread_id INTEGER,
                            std_grade TEXT,
                            taiko_grade TEXT,
                            ctb_grade TEXT,
                            mania_grade TEXT,
                            local_offset INTEGER,
                            stack_leniency NUMERIC,
                            gameplay_mode TEXT,
                            song_source TEXT,
                            song_tags TEXT,
                            online_offset INTEGER,
                            title_font TEXT,
                            unplayed INTEGER,
                            last_played INTEGER,
                            is_osz2 INTEGER,
                            folder_name TEXT,
                            last_checked TEXT,
                            ignore_sound INTEGER,
                            ignore_skin INTEGER,
                            disable_storyboard INTEGER,
                            disable_video INTEGER,
                            visual_override INTEGER,
                            unknown INTEGER,
                            last_modification2 TEXT,
                            mania_scroll_speed INTEGER
                        );""")

    def add_beatmap_to_db(self, beatmap: Beatmap):
        self.beatmaps_db.execute("INSERT INTO beatmaps VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                                 (beatmap.size, beatmap.artist, beatmap.artist_unicode, beatmap.title, beatmap.title_unicode,
                                  beatmap.mapper, beatmap.difficulty, beatmap.audio_file, beatmap.md5_hash, beatmap.osu_file,
                                  str(pickle.dumps(beatmap.ranked_status)), beatmap.count_hitcircles, beatmap.count_sliders, beatmap.count_spinners, str(pickle.dumps(beatmap.last_modification)),
                                  beatmap.ar, beatmap.cs, beatmap.hp, beatmap.od, beatmap.slider_velocity,
                                  str(pickle.dumps(beatmap.std_pairs)), str(pickle.dumps(beatmap.taiko_pairs)), str(pickle.dumps(beatmap.ctb_pairs)), str(pickle.dumps(beatmap.mania_pairs)),
                                  beatmap.drain_time, beatmap.total_time, beatmap.preview_time, str(pickle.dumps(beatmap.timing_points)), beatmap.difficulty_id, beatmap.beatmap_id,
                                  beatmap.thread_id, str(pickle.dumps(beatmap.std_grade)), str(pickle.dumps(beatmap.taiko_grade)), str(pickle.dumps(beatmap.ctb_grade)), str(pickle.dumps(beatmap.mania_grade)),
                                  beatmap.local_offset, beatmap.stack_leniency, str(pickle.dumps(beatmap.gameplay_mode)), beatmap.song_source, beatmap.song_tags,
                                  beatmap.online_offset, beatmap.title_font, beatmap.unplayed, str(pickle.dumps(beatmap.last_played)), beatmap.is_osz2,
                                  beatmap.folder_name, str(pickle.dumps(beatmap.last_checked)), beatmap.ignore_sound, beatmap.ignore_skin, beatmap.disable_storyboard,
                                  beatmap.disable_video, beatmap.visual_override, beatmap.unknown, beatmap.last_modification2, beatmap.mania_scroll_speed))

    def parse(self, connection: sqlite3.Connection = None, skip_beatmaps: bool = False) -> Osudb:
        game_version = utils.read_uint(self.osu_db_file)
        folder_count = utils.read_uint(self.osu_db_file)
        account_unlocked = utils.read_bool(self.osu_db_file)
        unlock_datetime = datetime.datetime.min + datetime.timedelta(microseconds=utils.read_ulong(self.osu_db_file) / 10)
        username = utils.read_string(self.osu_db_file)
        count_beatmaps = utils.read_uint(self.osu_db_file)

        self.beatmaps_db = connection
        if skip_beatmaps:
            for _ in range(count_beatmaps):
                Beatmap.parse(self.osu_db_file, game_version)
        else:
            self.generate_sql_db()
            for _ in range(count_beatmaps):
                self.add_beatmap_to_db(Beatmap.parse(self.osu_db_file, game_version))

            self.beatmaps_db.commit()

        user_permissions = UserPermissions(utils.read_uint(self.osu_db_file))

        return Osudb(game_version, folder_count, account_unlocked, unlock_datetime, username, count_beatmaps, self.beatmaps_db, user_permissions)


def parse_osudb(osudb_file: str | os.PathLike | io.BytesIO, beatmaps_db: str | os.PathLike = None, skip_beatmaps: bool = False) -> Osudb:
    if not isinstance(osudb_file, io.BytesIO):
        osudb_file = open(osudb_file, "rb")

    db_connection = None

    if beatmaps_db is None:
        db_connection = sqlite3.connect(tempfile.gettempdir() + "pyosudb_tmp.sql")
    else:
        db_connection = sqlite3.connect(beatmaps_db)

    return _Parser(osudb_file).parse(db_connection, skip_beatmaps)
