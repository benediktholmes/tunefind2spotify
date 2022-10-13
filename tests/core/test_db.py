"""Test module for `tunefind2spotify.core.db`."""

import datetime
import pytest
import _sqlite3

from tunefind2spotify.utils import MediaType

from tests.core import mock_db as db
from tests.test_data.mock_json_data import \
    MOCK_SHOW_JSON, \
    MOCK_MOVIE_JSON, \
    MOCK_GAME_JSON, _get_show_uris


def test_db_created_correctly():
    dbc = db.DBConnector()
    for table_name in ['media', 'songs', 'shows', 'match_show', 'match_other']:
        cursor = dbc._execute(f'SELECT name FROM sqlite_master WHERE type="table" AND name="{table_name}";')
        assert cursor.fetchall()


def test_db_reuse_created_file():
    _val = db.REUSE
    db.REUSE = True
    dbc = db.DBConnector()
    dbc.insert_json_data(MOCK_SHOW_JSON)
    del dbc
    dbc = db.DBConnector()
    assert dbc.media_exists(MOCK_SHOW_JSON['media_name'])
    db.REUSE = _val


def test_sqlite_error_during_execution():
    dbc = db.DBConnector()
    with pytest.raises(_sqlite3.Error):
        dbc._execute('SELECT')


def test_db_insert_json_show():
    dbc = db.DBConnector()
    dbc.insert_json_data(MOCK_SHOW_JSON)


def test_db_insert_json_show_double():
    dbc = db.DBConnector()
    dbc.insert_json_data(MOCK_SHOW_JSON)
    dbc.insert_json_data(MOCK_SHOW_JSON)


def test_db_insert_json_game():
    dbc = db.DBConnector()
    dbc.insert_json_data(MOCK_GAME_JSON)


def test_db_insert_json_game_double():
    dbc = db.DBConnector()
    dbc.insert_json_data(MOCK_GAME_JSON)
    dbc.insert_json_data(MOCK_GAME_JSON)


def test_get_track_uris_show():
    dbc = db.DBConnector()
    dbc.insert_json_data(MOCK_SHOW_JSON)
    uris = dbc.get_track_uris_show(MOCK_SHOW_JSON['media_name'])
    for suffix in [x.split(':')[-1] for x in _get_show_uris()]:
        assert f'spotify:track:{suffix}' in uris, \
            f'URI spotify:track:{suffix} expected to be retrieved for mock data \'{MOCK_SHOW_JSON["media_name"]}\' .'


def test_get_track_uris_show_restricted():
    dbc = db.DBConnector()
    dbc.insert_json_data(MOCK_SHOW_JSON)
    uris = dbc.get_track_uris_show(MOCK_SHOW_JSON['media_name'], restrict_to_season=1)
    for suffix in [x.split(':')[-1] for x in _get_show_uris()]:
        if suffix == 'empty':
            continue
        assert f'spotify:track:{suffix}' in uris, \
            f'URI spotify:track:{suffix} expected to be retrieved for season 1 of \'{MOCK_SHOW_JSON["media_name"]}\' .'
    uris = dbc.get_track_uris_show(MOCK_SHOW_JSON['media_name'], restrict_to_season=2)
    for suffix in ['empty']:
        if suffix != 'empty':
            continue
        assert f'spotify:track:{suffix}' in uris, \
            f'URI spotify:track:{suffix} expected to be retrieved for season 2 of \'{MOCK_SHOW_JSON["media_name"]}\' .'


def test_get_track_uris_show_restrict_fails():
    dbc = db.DBConnector()
    dbc.insert_json_data(MOCK_SHOW_JSON)
    with pytest.raises(ValueError):
        dbc.get_track_uris_show(MOCK_SHOW_JSON['media_name'], restrict_to_season=-1)
        dbc.get_track_uris_show(MOCK_SHOW_JSON['media_name'], restrict_to_season=len(MOCK_SHOW_JSON['seasons']) + 10)


def test_get_track_uris_media():
    dbc = db.DBConnector()
    dbc.insert_json_data(MOCK_GAME_JSON)
    uris = dbc.get_track_uris_media(MOCK_GAME_JSON['media_name'])
    for suffix in [x.split(':')[-1] for x in _get_show_uris()]:
        assert f'spotify:track:{suffix}' in uris, \
            f'URI spotify:track:{suffix} expected to be retrieved for mock data \'{MOCK_GAME_JSON["media_name"]}\' .'


def test_get_media_type():
    dbc = db.DBConnector()
    dbc.insert_json_data(MOCK_SHOW_JSON)
    dbc.insert_json_data(MOCK_MOVIE_JSON)
    dbc.insert_json_data(MOCK_GAME_JSON)
    x = dbc.get_media_type(MOCK_SHOW_JSON['media_name'])
    assert x == MediaType.SHOW, f'Expected MediaType.SHOW . Instead got: {x} .'
    x = dbc.get_media_type(MOCK_MOVIE_JSON['media_name'])
    assert x == MediaType.MOVIE, f'Expected MediaType.MOVIE . Instead got: {x} .'
    x = dbc.get_media_type(MOCK_GAME_JSON['media_name'])
    assert x == MediaType.GAME, f'Expected MediaType.GAME . Instead got: {x} .'


def test_get_last_updated():
    dbc = db.DBConnector()
    dbc.insert_json_data(MOCK_SHOW_JSON)
    dbc.insert_json_data(MOCK_GAME_JSON)
    time_diff_sec = dbc.get_last_updated(MOCK_SHOW_JSON['media_name']) - int(datetime.datetime.now().timestamp())
    assert time_diff_sec < 2, f'Expected timestamp in db to be current. Time difference too big: {time_diff_sec} [sec].'
    time_diff_sec = dbc.get_last_updated(MOCK_GAME_JSON['media_name']) - int(datetime.datetime.now().timestamp())
    assert time_diff_sec < 2, f'Expected timestamp in db to be current. Time difference too big: {time_diff_sec} [sec].'


def test_db_deconstructor():
    dbc = db.DBConnector()
    del dbc
