from dataclasses import dataclass
from typing import Union, Any, List
import datetime
import tempfile
import sqlite3
import pickle
import io
import os

from pyosutools import utils
from pyosutools.db.datatypes import Beatmap, UserPermissions, RankedStatus, ModStarRatingPair, TimingPoint
from pyosutools.datatypes import Mod, GameMode


@dataclass
class Osudb:
    """
    Class representing osu!.db file

    Attributes
    ----
    game_version: int
        osu! version when this file created

    account_unlocked: bool
        Is account banned. False if banned, True otherwise

    unlock_datetime: datetime.datetime
        Time until account will be unbanned. Always 0 if account is not banned (account_unlocked=True)

    username: str
        Player username

    sql_beatmaps_db: sqlite3.Connection
        Connection to sqllite3 database. It must not be set by the user

    user_permissions: UserPermissions
        User permissions in chat. Check UserPermissions class for more info
    """
    game_version: int
    account_unlocked: bool  # false if account banned/locked
    unlock_datetime: datetime.datetime
    username: str

    sql_beatmaps_db: sqlite3.Connection

    user_permissions: UserPermissions

    # can't be saved because osu.db can be big and we don't need 20k objects with maps in our ram
    def beatmaps(self) -> List[Beatmap]:
        """
        List of beatmaps

        Returns
        ----
        List[Beatmaps]
            List of Beatmaps instances
        """
        cursor = self.sql_beatmaps_db.cursor()
        return [Beatmap.from_sql(*beatmap) for beatmap in cursor.execute("SELECT * FROM 'beatmaps' ").fetchall()]

    def get_beatmap_from_hash(self, hash: str) -> Beatmap:
        """
        Get beatmap from sql table using hash

        Args
        ----
        hash: str
            beatmap hash

        Returns
        ----
        Beatmap
            instance of Beatmap
        """
        cursor = self.sql_beatmaps_db.cursor()
        return _Parser.beatmap_from_sql(*cursor.execute(f"SELECT * FROM 'beatmaps' WHERE md5_hash='{hash}'").fetchone())

    def beatmaps_execute_sql(self, command) -> Any:
        """
        Executes sql command in table with beatmaps
        """
        cursor = self.sql_beatmaps_db.cursor()
        return cursor.execute(command).fetchall()


class _Parser:
    def __init__(self, osu_db_file) -> None:
        self.osu_db_file = osu_db_file
        self.offset = 0

    def generate_sql_db(self) -> None:
        """
        Generates sql table for file
        """
        cursor = self.beatmaps_db.cursor()
        cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='beatmaps'")
        if cursor.fetchone()[0] == 1:
            self.beatmaps_db.execute("DROP TABLE beatmaps")
        self.beatmaps_db.execute("""CREATE TABLE beatmaps (
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
                            mania_scroll_speed INTEGER
                        );""")

    def add_beatmap_to_db(self, beatmap: Beatmap) -> None:
        """
        Adds beatmap to sql table
        """
        self.beatmaps_db.execute("INSERT INTO beatmaps VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                                 (beatmap.artist, beatmap.artist_unicode, beatmap.title, beatmap.title_unicode,
                                  beatmap.mapper, beatmap.difficulty, beatmap.audio_file, beatmap.md5_hash, beatmap.osu_file,
                                  str(pickle.dumps(beatmap.ranked_status)), beatmap.count_hitcircles, beatmap.count_sliders, beatmap.count_spinners, str(pickle.dumps(beatmap.last_modification)),
                                  beatmap.ar, beatmap.cs, beatmap.hp, beatmap.od, beatmap.slider_velocity,
                                  str(pickle.dumps(beatmap.std_pairs)), str(pickle.dumps(beatmap.taiko_pairs)), str(pickle.dumps(beatmap.ctb_pairs)), str(pickle.dumps(beatmap.mania_pairs)),
                                  beatmap.drain_time, beatmap.total_time, beatmap.preview_time, str(pickle.dumps(beatmap.timing_points)), beatmap.difficulty_id, beatmap.beatmap_id,
                                  beatmap.thread_id, str(pickle.dumps(beatmap.std_grade)), str(pickle.dumps(beatmap.taiko_grade)), str(pickle.dumps(beatmap.ctb_grade)), str(pickle.dumps(beatmap.mania_grade)),
                                  beatmap.local_offset, beatmap.stack_leniency, str(pickle.dumps(beatmap.gameplay_mode)), beatmap.song_source, beatmap.song_tags,
                                  beatmap.online_offset, beatmap.title_font, beatmap.unplayed, str(pickle.dumps(beatmap.last_played)), beatmap.is_osz2,
                                  beatmap.folder_name, str(pickle.dumps(beatmap.last_checked)), beatmap.ignore_sound, beatmap.ignore_skin, beatmap.disable_storyboard,
                                  beatmap.disable_video, beatmap.visual_override, beatmap.mania_scroll_speed))

    def parse(self, connection: sqlite3.Connection = None, skip_beatmaps: bool = False) -> Osudb:
        game_version = utils.read_uint(self.osu_db_file)
        utils.read_uint(self.osu_db_file)  # ignoring folder count cuz we don't need it
        account_unlocked = utils.read_bool(self.osu_db_file)
        unlock_datetime = utils.read_datetime(self.osu_db_file)
        username = utils.read_string(self.osu_db_file)

        count_beatmaps = utils.read_uint(self.osu_db_file)

        self.beatmaps_db = connection
        if skip_beatmaps:
            for _ in range(count_beatmaps):
                self.parse_beatmap(game_version)
        else:
            self.generate_sql_db()
            for _ in range(count_beatmaps):
                self.add_beatmap_to_db(self.parse_beatmap(game_version))

            self.beatmaps_db.commit()

        user_permissions = UserPermissions(utils.read_uint(self.osu_db_file))

        return Osudb(game_version, account_unlocked, unlock_datetime, username, self.beatmaps_db, user_permissions)

    def parse_beatmap(self, game_ver: int = 0):
        """
        Parse beatmap

        Args
        ----
        game_ver: int
            Version of game

        Returns
        ----
        Beatmap
            Parsed beatmap instance
        """
        if game_ver < 20191106:
            utils.read_uint(self.osu_db_file)  # ignore size
        artist = utils.read_string(self.osu_db_file)
        artist_unicode = utils.read_string(self.osu_db_file)
        title = utils.read_string(self.osu_db_file)

        title_unicode = utils.read_string(self.osu_db_file)
        creator = utils.read_string(self.osu_db_file)
        difficulty = utils.read_string(self.osu_db_file)
        audio_file = utils.read_string(self.osu_db_file)
        md5_hash = utils.read_string(self.osu_db_file)
        osu_file = utils.read_string(self.osu_db_file)

        ranked_status = RankedStatus(utils.read_ubyte(self.osu_db_file))
        count_hitcircles = utils.read_ushort(self.osu_db_file)
        count_sliders = utils.read_ushort(self.osu_db_file)
        count_spiners = utils.read_ushort(self.osu_db_file)

        last_modification = utils.read_datetime(self.osu_db_file)

        if game_ver < 20140609:
            ar = utils.read_ubyte(self.osu_db_file)
            cs = utils.read_ubyte(self.osu_db_file)
            hp = utils.read_ubyte(self.osu_db_file)
            od = utils.read_ubyte(self.osu_db_file)
        else:
            ar = utils.read_float(self.osu_db_file)
            cs = utils.read_float(self.osu_db_file)
            hp = utils.read_float(self.osu_db_file)
            od = utils.read_float(self.osu_db_file)

        slider_velocity = utils.read_double(self.osu_db_file)

        std_pairs = []
        taiko_pairs = []
        ctb_pairs = []
        mania_pairs = []
        if game_ver >= 20140609:
            for _ in range(utils.read_uint(self.osu_db_file)):
                tmp = utils.read_int_double(self.osu_db_file)
                std_pairs.append(ModStarRatingPair(Mod(tmp[0]), tmp[1]))

            for _ in range(utils.read_uint(self.osu_db_file)):
                tmp = utils.read_int_double(self.osu_db_file)
                taiko_pairs.append(ModStarRatingPair(Mod(tmp[0]), tmp[1]))

            for _ in range(utils.read_uint(self.osu_db_file)):
                tmp = utils.read_int_double(self.osu_db_file)
                ctb_pairs.append(ModStarRatingPair(Mod(tmp[0]), tmp[1]))

            for _ in range(utils.read_uint(self.osu_db_file)):
                tmp = utils.read_int_double(self.osu_db_file)
                mania_pairs.append(ModStarRatingPair(Mod(tmp[0]), tmp[1]))

        drain_time = utils.read_uint(self.osu_db_file)
        total_time = utils.read_uint(self.osu_db_file)
        preview_time = utils.read_uint(self.osu_db_file)

        timing_points = []
        for _ in range(utils.read_uint(self.osu_db_file)):
            timing_points.append(TimingPoint(*utils.read_timing_point(self.osu_db_file)))

        difficulty_id = utils.read_uint(self.osu_db_file)
        beatmap_id = utils.read_uint(self.osu_db_file)
        thread_id = utils.read_uint(self.osu_db_file)

        std_grade = utils.read_ubyte(self.osu_db_file)
        taiko_grade = utils.read_ubyte(self.osu_db_file)
        ctb_grade = utils.read_ubyte(self.osu_db_file)
        mania_grade = utils.read_ubyte(self.osu_db_file)

        local_offset = utils.read_ushort(self.osu_db_file)
        stack_laniency = utils.read_float(self.osu_db_file)

        gameplay_mode = GameMode(utils.read_ubyte(self.osu_db_file))

        song_source = utils.read_string(self.osu_db_file)
        song_tags = utils.read_string(self.osu_db_file)

        online_offset = utils.read_ushort(self.osu_db_file)

        title_font = utils.read_string(self.osu_db_file)

        unplayed = utils.read_bool(self.osu_db_file)
        last_played = utils.read_datetime(self.osu_db_file)

        is_osz2 = utils.read_bool(self.osu_db_file)
        folder_name = utils.read_string(self.osu_db_file)
        last_checked = utils.read_datetime(self.osu_db_file)

        ignore_sound = utils.read_bool(self.osu_db_file)
        ignore_skin = utils.read_bool(self.osu_db_file)
        disable_storyboard = utils.read_bool(self.osu_db_file)
        disable_video = utils.read_bool(self.osu_db_file)

        visual_override = utils.read_bool(self.osu_db_file)

        if game_ver < 20140609:
            utils.read_uint(self.osu_db_file)  # osu! wiki page literally says it's unknown and present if game version less than 20140609

        utils.read_uint(self.osu_db_file)  # ignore second modification time

        mania_scroll_speed = utils.read_ubyte(self.osu_db_file)

        return Beatmap(artist, artist_unicode, title, title_unicode, creator, difficulty, audio_file, md5_hash, osu_file, ranked_status, count_hitcircles, count_sliders,
                       count_spiners, last_modification, ar, cs, hp, od, slider_velocity, std_pairs, taiko_pairs, ctb_pairs, mania_pairs, drain_time, total_time, preview_time,
                       timing_points, difficulty_id, beatmap_id, thread_id, std_grade, taiko_grade, ctb_grade, mania_grade, local_offset, stack_laniency, gameplay_mode, song_source,
                       song_tags, online_offset, title_font, unplayed, last_played, is_osz2, folder_name, last_checked, ignore_sound, ignore_skin, disable_storyboard, disable_video,
                       visual_override, mania_scroll_speed)

    @staticmethod
    def beatmap_from_sql(*args):
        # TODO: rewrite func cuz this one is kinda unsave
        """
        Get beatmap from sql row

        Returns
        ----
        Beatmap
            osu! beatmap
        """
        new_args = []
        for arg in args:
            if arg is None:
                new_args.append(arg)
                continue

            if type(arg) == str and (arg[:2] == "b\'" or arg[:2] == "b\""):
                new_args.append(pickle.loads(bytearray(eval(arg))))
                continue
            new_args.append(arg)

        return Beatmap(*new_args)


def parse_osudb(osudb_file: Union[str, os.PathLike, io.BytesIO], beatmaps_db: Union[str, os.PathLike] = None, skip_beatmaps: bool = False, sql_check_same_thread: bool = True) -> Osudb:
    """
    Parse osu!.db file

    Args
    ----
    osudb_file: str | os.PathLike | io.BytesIO
        Path or opened file

    beatmaps_db: str | os.PathLike = None
        Path to sql database with beatmaps. \n
        If None - creates temp file in system temp directory  \n
        If non existing file, creates new one in that path  \n
        If existing file, opens it  \n

    skip_beatmaps: bool = False
        Skip beatmap parsing. \n
        Can decrease time for parsing, but beatmaps will be not available to use \n
        (except if beatmaps_db is profided with existing file)

    Returns
    ----
    Osudb
        instance of Osudb class
    """
    if not isinstance(osudb_file, io.BytesIO):
        osudb_file = open(osudb_file, "rb")

    db_connection = None

    if beatmaps_db is None:
        db_connection = sqlite3.connect(tempfile.gettempdir() + "pyosudb_tmp.sql", check_same_thread=sql_check_same_thread)
    else:
        db_connection = sqlite3.connect(beatmaps_db, check_same_thread=sql_check_same_thread)

    return _Parser(osudb_file).parse(db_connection, skip_beatmaps)
