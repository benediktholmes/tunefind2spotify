"""Test module for `tunefind2spotify.api`."""

import os

from tests import mock_api as api
from tests.test_data.mock_json_data import \
    MOCK_SHOW_JSON, \
    MOCK_MOVIE_JSON, \
    MOCK_GAME_JSON

CREDENTIALS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'test_data',
                                'mock_credentials'
                                ), 'r').readline()


def test_fetch():
    api.fetch(MOCK_SHOW_JSON['media_name'])
    api.fetch(MOCK_MOVIE_JSON['media_name'])
    api.fetch(MOCK_GAME_JSON['media_name'])


def test_export_without_fetch():
    api.string_capture.reset()
    api.export(MOCK_SHOW_JSON['media_name'], credentials=CREDENTIALS)
    assert api.string_capture.getvalue().split(os.linesep)[-2].startswith('WARNING')

    api.string_capture.reset()
    api.export(MOCK_MOVIE_JSON['media_name'], credentials=CREDENTIALS)
    assert api.string_capture.getvalue().split(os.linesep)[-2].startswith('WARNING')

    api.string_capture.reset()
    api.export(MOCK_GAME_JSON['media_name'], credentials=CREDENTIALS)
    assert api.string_capture.getvalue().split(os.linesep)[-2].startswith('WARNING')


def test_export_with_fetch():
    _val = api.db.REUSE
    api.db.REUSE = True

    api.fetch(MOCK_SHOW_JSON['media_name'])
    assert api.db.DBConnector().media_exists(MOCK_SHOW_JSON['media_name'])
    api.string_capture.reset()
    api.export(MOCK_SHOW_JSON['media_name'], credentials=CREDENTIALS)
    assert not api.string_capture.getvalue()

    api.fetch(MOCK_MOVIE_JSON['media_name'])
    assert api.db.DBConnector().media_exists(MOCK_MOVIE_JSON['media_name'])
    api.string_capture.reset()
    api.export(MOCK_MOVIE_JSON['media_name'], credentials=CREDENTIALS)
    assert not api.string_capture.getvalue()

    api.fetch(MOCK_GAME_JSON['media_name'])
    assert api.db.DBConnector().media_exists(MOCK_GAME_JSON['media_name'])
    api.string_capture.reset()
    api.export(MOCK_GAME_JSON['media_name'], credentials=CREDENTIALS)
    assert not api.string_capture.getvalue()

    api.db.REUSE = _val


def test_pull():
    _val = api.db.REUSE
    api.db.REUSE = True

    api.pull(MOCK_SHOW_JSON['media_name'], credentials=CREDENTIALS)
    assert api.db.DBConnector().media_exists(MOCK_SHOW_JSON['media_name'])
    api.pull(MOCK_MOVIE_JSON['media_name'], credentials=CREDENTIALS)
    assert api.db.DBConnector().media_exists(MOCK_MOVIE_JSON['media_name'])
    api.pull(MOCK_GAME_JSON['media_name'], credentials=CREDENTIALS)
    assert api.db.DBConnector().media_exists(MOCK_GAME_JSON['media_name'])

    api.db.REUSE = _val
