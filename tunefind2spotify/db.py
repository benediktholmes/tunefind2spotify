"""Database module.

This module handles caching of relevant data scraped from Tunefind in a local
database. A connector class serves as abstraction layer for easy data insertion
and retrieval. The database scheme is build up as follows:

- the `media` table lists the name and type of the media scraped from tunefind.

- the `songs` table is a record of all the songs that were scraped by this tool.

- the `match_*` tables serve as NxM references of which songs appear with which
  media.

Opposed to other media types, type `show` has a secondary layer due to the
separation into seasons. To capture this, `show` media is recorded in additional
tables:

- the `shows` table lists the different seasons each show has.

- other than the `match_other` table, which is a NxM reference of primary keys
  from the `media` and `songs` table, the `match shows` table is a NxM reference
  of primary keys from tables `shows` and `songs`, thereby effectively retaining
  the data granularity.

Attributes:
    DEFAULT_DB_FIELPATH (str): Path to default database file.
    SQL_CREATE_MEDIA_TABLE (str): SQL instruction to create respective table.
    SQL_CREATE_SONGS_TABLE (str): SQL instruction to create respective table.
    SQL_CREATE_SHOWS_TABLE (str): SQL instruction to create respective table.
    SQL_CREATE_MATCH_SHOW_TABLE (str): SQL instruction to create respective
        table.
    SQL_CREATE_MATCH_OTHER_TABLE (str): SQL instruction to create respective
        table.

"""

import os
import sqlite3

from datetime import datetime
from sqlite3 import Error
from typing import List, Optional

from tunefind2spotify.utils import MediaType, singleton


DEFAULT_DB_FILEPATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'data',
        'tunefind_sqlite.db')


SQL_CREATE_MEDIA_TABLE = """CREATE TABLE IF NOT EXISTS media (
                            id integer PRIMARY KEY AUTOINCREMENT,
                            media_name text NOT NULL,
                            media_type text NOT NULL,
                            last_updated integer NOT NULL
                            ); """

SQL_CREATE_SONGS_TABLE = """CREATE TABLE IF NOT EXISTS songs (
                            id integer PRIMARY KEY AUTOINCREMENT,
                            song_name text NOT NULL,
                            artists text NOT NULL,
                            tunefind_id integer NOT NULL,
                            spotify_uri text NOT NULL
                            );"""

SQL_CREATE_SHOWS_TABLE = """CREATE TABLE IF NOT EXISTS shows (
                            id integer PRIMARY KEY AUTOINCREMENT,
                            season integer NOT NULL,
                            episode integer NOT NULL,
                            tunefind_id integer NOT NULL,
                            media_id integer NOT NULL,
                            FOREIGN KEY (media_id) REFERENCES media (id)
                            );"""

SQL_CREATE_MATCH_SHOW_TABLE = """CREATE TABLE IF NOT EXISTS match_show (
                                id integer PRIMARY KEY AUTOINCREMENT,
                                episode_id integer NOT NULL,
                                song_id integer NOT NULL,
                                FOREIGN KEY (episode_id) REFERENCES shows (id),
                                FOREIGN KEY (song_id) REFERENCES songs (id)
                                );"""

SQL_CREATE_MATCH_OTHER_TABLE = """CREATE TABLE IF NOT EXISTS match_other (
                                id integer PRIMARY KEY AUTOINCREMENT,
                                media_id integer NOT NULL,
                                song_id integer NOT NULL,
                                FOREIGN KEY (media_id) REFERENCES media (id),
                                FOREIGN KEY (song_id) REFERENCES songs (id)
                                );"""


def create_connection(db_file: str) -> sqlite3.Connection:
    """Creates a database connection via SQLite.

    Args:
        db_file: Name of database file.

    Returns:
        A sqlite3.Connection object.

    Raises:
        TODO
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)  # TODO: Log
    return conn


def create_table(conn: sqlite3.Connection, create_table_sql: str) -> None:
    """Creates a table from the create_table_sql statement.

    TODO: Careful: Any SQL command could be passed to this function!

    Args:
        conn: The connection object referencing the database in which to add the
            new table.
        create_table_sql: SQL statement to be executed.

    Raises:
        TODO
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)  # TODO: log


@singleton
class DBConnector:
    """Handler for access to database.

    Attributes:
        conn (sqlite3.Connection): Database connection object.
    """

    def __init__(self, db_filepath: Optional[str] = DEFAULT_DB_FILEPATH) -> None:
        """Opens connection to local database and ensures creation of tables.

        Args:
            db_filepath: Full path to database file. Optional, defaults to
            `DEFAULT_DB_FILEPATH`.
        """
        path = os.path.dirname(db_filepath)
        if not os.path.isdir(path):
            os.mkdir(path)
        self.conn = create_connection(db_filepath)
        create_table(self.conn, SQL_CREATE_MEDIA_TABLE)
        create_table(self.conn, SQL_CREATE_SONGS_TABLE)
        create_table(self.conn, SQL_CREATE_SHOWS_TABLE)
        create_table(self.conn, SQL_CREATE_MATCH_SHOW_TABLE)
        create_table(self.conn, SQL_CREATE_MATCH_OTHER_TABLE)

    def insert_json_data(self, data: dict) -> None:
        """Inserts data from nested dictionary into database.

        Note:
            Schema of the nested dictionary is assumed. This is bad style.

        Args:
            data: Nested dictionary holding data to be inserted into database.
        """
        media_prim_key = self._insert_media(media_name=data['media_name'],
                                            media_type=data['media_type'])
        if data['media_type'] == MediaType.SHOW:
            epsids = []
            song_prim_keys = []
            # add new songs to songs:
            for s in data['seasons']:
                e_ids = []
                song_s_prim_keys = []
                for e in s['episodes']:
                    song_e_prim_keys = []
                    e_ids.append(e['id'])
                    for song in e['songs']:
                        song_prim_key = self._insert_song(song_name=song['name'],
                                                          artists=song['artists'],
                                                          tunefind_id=song['id'],
                                                          spotify_uri=song['spotify'])
                        song_e_prim_keys.append(song_prim_key)
                    song_s_prim_keys.append(song_e_prim_keys)
                epsids.append(e_ids)
                song_prim_keys.append(song_s_prim_keys)
            # use returned ids to reference songs in songs table
            show_prim_keys = self._insert_show(media_foreign_key=media_prim_key, episode_ids=epsids)
            # update references in match_show
            for i in range(len(song_prim_keys)):
                for j in range(len(song_prim_keys[i])):
                    for k in range(len(song_prim_keys[i][j])):
                        self._insert_match(x_foreign_key=show_prim_keys[i][j],
                                           song_foreign_key=song_prim_keys[i][j][k],
                                           media_type=data['media_type'])
        else:
            # add new songs to songs:
            song_prim_keys = []
            for song in data['songs']:
                song_prim_key = self._insert_song(song_name=song['name'],
                                                  artists=song['artists'],
                                                  tunefind_id=song['id'],
                                                  spotify_uri=song['spotify'])
                song_prim_keys.append(song_prim_key)
            # update references in match_other
            for i in range(len(song_prim_keys)):
                self._insert_match(x_foreign_key=media_prim_key,
                                   song_foreign_key=song_prim_keys[i],
                                   media_type=data['media_type'])

    def _insert_media(self,
                      media_name: str,
                      media_type: MediaType) -> int:
        """Inserts new media entry (if not exists) into media table.

        Args:
            media_name: Name of media to be inserted in media table.
            media_type: Type of media to be inserted in media table.

        Returns:
            Primary key of entry in media table.
        """
        cur = self.conn.cursor()
        sql = f'SELECT * FROM media WHERE media_name=="{media_name}"'
        cur.execute(sql)
        rows = cur.fetchall()
        assert len(rows) <= 1  # There should be at most one result as the media names are unique on Tunefind.
        if rows:
            return rows[0][0]
        else:
            sql = 'INSERT INTO media(media_name,media_type,last_updated) VALUES(?,?,?)'
            cur.execute(sql, [media_name, media_type, int(datetime.now().timestamp())])
            self.conn.commit()
            return cur.lastrowid

    def _insert_song(self,
                     song_name: str,
                     artists: str,
                     tunefind_id: int,
                     spotify_uri: str) -> int:
        """Inserts new song entry (if not exists) into songs table.

        Args:
            song_name: Name of the song.
            artists: String of comma-separated artist names.
            tunefind_id: The unique id of the song on Tunefind.
            spotify_uri: The URI of the song on Spotify.

        Returns:
            Primary key of entry in songs table.
        """
        cur = self.conn.cursor()
        sql = f"""SELECT *
                  FROM songs
                  WHERE tunefind_id=="{tunefind_id}"
               """
        cur.execute(sql)
        rows = cur.fetchall()
        assert len(rows) <= 1, rows  # There should be at most one result as the Tunefind ID are unique.
        if rows:
            return rows[0][0]
        else:
            sql = 'INSERT INTO songs(song_name,artists,tunefind_id,spotify_uri) VALUES(?,?,?,?)'
            cur = self.conn.cursor()
            cur.execute(sql, [song_name, artists, tunefind_id, spotify_uri])
            self.conn.commit()
            return cur.lastrowid

    def _insert_show(self,
                     media_foreign_key: int,
                     episode_ids: List[List[int]]) -> List[List[int]]:
        """Inserts new show entry (if not exists) into shows table.

        Args:
            media_foreign_key: Primary key of respective media in media table.
            episode_ids: Nested list of unique Tunefind ids for each episode.
                First axis iterates over seasons, second over the episodes in
                each season.

        Returns:
            List of primary keys of entry in show table wrt. to season order.
        """
        cur = self.conn.cursor()
        prim_keys = []
        for s, e_ids in enumerate(episode_ids):
            eps_keys = []
            for e, e_id in enumerate(e_ids):
                sql = f"""SELECT *
                          FROM shows
                          WHERE media_id=="{media_foreign_key}"
                          AND season=="{s+1}"
                          AND episode=="{e+1}"
                      """
                cur.execute(sql)
                rows = cur.fetchall()
                assert len(rows) <= 1  # There should be at most one result.
                if rows:
                    eps_keys.append(rows[0][0])
                else:
                    sql = 'INSERT INTO shows(season,episode,tunefind_id,media_id) VALUES(?,?,?,?)'
                    cur.execute(sql, [s + 1, e + 1, e_id, media_foreign_key])
                    self.conn.commit()
                    eps_keys.append(cur.lastrowid)
            prim_keys.append(eps_keys)
        return prim_keys

    def _insert_match(self,
                      x_foreign_key: int,
                      song_foreign_key: int,
                      media_type: MediaType) -> int:
        """Inserts match entry into match_show or match_other table.

        Args:
            x_foreign_key: Primary key of either media (media table) or episode
                (show table) to which the song will be referenced. Dependent on
                media type.
            song_foreign_key: Primary key of the respective song.
            media_type: Type of the media. Required to distinguish table in
                which to insert the match data.

        Returns:
            Primary key of entry in corresponding match table.
        """
        cur = self.conn.cursor()
        if media_type == MediaType.SHOW:
            sql = f'SELECT * FROM match_show WHERE episode_id=="{x_foreign_key}" AND song_id=="{song_foreign_key}"'
            cur.execute(sql)
            rows = cur.fetchall()
            assert len(rows) <= 1  # There should be at most one result.
            if rows:
                return rows[0][0]
            else:
                sql_show = 'INSERT INTO match_show(episode_id,song_id) VALUES(?,?)'
                cur.execute(sql_show, [x_foreign_key, song_foreign_key])
                self.conn.commit()
        else:
            sql = f'SELECT * FROM match_other WHERE media_id=="{x_foreign_key}" AND song_id=="{song_foreign_key}"'
            cur.execute(sql)
            rows = cur.fetchall()
            assert len(rows) <= 1  # There should be at most one result.
            if rows:
                return rows[0][0]
            else:
                sql_other = 'INSERT INTO match_other(media_id,song_id) VALUES(?,?)'
                cur.execute(sql_other, [x_foreign_key, song_foreign_key])
                self.conn.commit()
        return cur.lastrowid

    def get_track_uris_media(self, media_name: str) -> List[str]:
        """Retrieves song URIs from database referencing to given media name.

        Args:
            media_name: Name of the media name.

        Returns:
            List of song URI referenced by media name.
        """
        sql = f"""SELECT spotify_uri
                  FROM songs
                  JOIN match_other ON songs.id=match_other.song_id
                  JOIN media ON media.id=match_other.media_id
                  WHERE media.media_name=="{media_name}"
              """
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        return [x[0] for x in rows if x[0]]

    def get_track_uris_show(self,
                            media_name: str,
                            restrict_to_season: Optional[int] = None) -> List[str]:
        """Retrieves song URIs from database referencing to given media name.

        Note:
            This method is specialized for media of type `show` and offers an
            optional argument to restrict retrieval to a specific season.

        Args:
            media_name: Name of the media.
            restrict_to_season: Only returns URIs for a specified season. Season
                enumeration starts at 1. Optional, defaults to None in which
                case URIs across all seasons are returned.

        Returns:
            List of song URI referenced by media name.
        """
        cur = self.conn.cursor()
        if restrict_to_season is not None:
            sql = f"""SELECT *
                      FROM shows
                      JOIN media ON media.id=shows.media_id
                      WHERE media.media_name=="{media_name}" AND shows.season=="{restrict_to_season}"
                  """
            cur.execute(sql)
            rows = cur.fetchall()
            if not rows:
                raise Exception(f'Parameter `restrict-to-season` out-of-bounds with value: {restrict_to_season}')
        sql = f"""SELECT spotify_uri
                  FROM songs
                  JOIN match_show ON songs.id=match_show.song_id
                  JOIN shows ON shows.id=match_show.episode_id
                  JOIN media ON media.id=shows.media_id
                  WHERE media.media_name=="{media_name}"
              """
        sql_restriction = f' AND shows.season={restrict_to_season}'
        if restrict_to_season is not None:
            sql += sql_restriction
        cur.execute(sql)
        rows = cur.fetchall()
        return [x[0] for x in rows if x[0]]

    def get_media_type(self, media_name: str) -> MediaType:
        """Retrieves media type stored in media table for given media name.

        Args:
            media_name: Name of the media.

        Returns:
            Type of the media specified by name.
        """
        cur = self.conn.cursor()
        sql = f"""SELECT media_type
                  FROM media
                  WHERE media_name=="{media_name}"
              """
        cur.execute(sql)
        rows = cur.fetchall()
        return MediaType(int(rows[0][0]))

    def __del__(self) -> None:
        self.conn.close()
