import copy
import os
import pytest

from tests import mock_main as main
from tests.test_data.mock_json_data import \
    MOCK_SHOW_JSON, \
    MOCK_MOVIE_JSON, \
    MOCK_GAME_JSON, \
    MOCK_SHOW_JSON_NAME_NORM, \
    MOCK_MOVIE_JSON_NAME_NORM, \
    MOCK_GAME_JSON_NAME_NORM


def test_find_credentials_delimiter():
    with pytest.raises(ValueError):
        main.find_credentials(delimiter='')
    with pytest.raises(ValueError):
        main.find_credentials(delimiter='ABC')


def test_find_credentials_unpack():
    _copy_args = copy.deepcopy(main.ARGS)
    main.__setattr__('ARGS', {'credentials': 'ABC'})
    with pytest.raises(ValueError):
        main.find_credentials()
    main.__setattr__('ARGS', _copy_args)


def test_find_credentials_in_params():
    _copy_args = copy.deepcopy(main.ARGS)
    main.__setattr__('ARGS', {'credentials': 'USERID|SECRET|REDIRECT_URI'})
    i, s, r = main.find_credentials()
    assert i == 'USERID'
    assert s == 'SECRET'
    assert r == 'REDIRECT_URI'
    main.__setattr__('ARGS', _copy_args)


def test_find_credentials_in_env():
    os.environ['SPOTIPY_CLIENT_ID'] = 'USERID'
    os.environ['SPOTIPY_CLIENT_SECRET'] = 'SECRET'
    os.environ['SPOTIPY_REDIRECT_URI'] = 'REDIRECT_URI'
    i, s, r = main.find_credentials()
    assert i == 'USERID'
    assert s == 'SECRET'
    assert r == 'REDIRECT_URI'
    del os.environ['SPOTIPY_CLIENT_ID']
    del os.environ['SPOTIPY_CLIENT_SECRET']
    del os.environ['SPOTIPY_REDIRECT_URI']


def test_find_credentials_in_file_specified():
    _copy_args = copy.deepcopy(main.ARGS)
    main.__setattr__('ARGS', {'cred-file': os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                        'test_data',
                                                        'mock_credentials'
                                                        )})
    i, s, r = main.find_credentials()
    assert i == 'USERID'
    assert s == 'SECRET'
    assert r == 'REDIRECT_URI'
    main.__setattr__('ARGS', _copy_args)


def test_find_credentials_not_found():
    _copy_args = copy.deepcopy(main.ARGS)
    main.__setattr__('ARGS', {})
    with pytest.raises(main.MissingCredentialsException):
        main.find_credentials()
    main.__setattr__('ARGS', _copy_args)


def test_fetch():
    main.fetch(MOCK_SHOW_JSON['media_name'])
    main.fetch(MOCK_MOVIE_JSON['media_name'])
    main.fetch(MOCK_GAME_JSON['media_name'])


def test_export_without_fetch():
    _copy_args = copy.deepcopy(main.ARGS)
    main.__setattr__('ARGS', {'credentials': 'USERID|SECRET|REDIRECT_URI'})

    main.string_capture.reset()
    main.export(MOCK_SHOW_JSON_NAME_NORM)
    assert main.string_capture.getvalue().split(os.linesep)[-2].startswith('WARNING')

    main.string_capture.reset()
    main.export(MOCK_MOVIE_JSON_NAME_NORM)
    assert main.string_capture.getvalue().split(os.linesep)[-2].startswith('WARNING')

    main.string_capture.reset()
    main.export(MOCK_GAME_JSON_NAME_NORM)
    assert main.string_capture.getvalue().split(os.linesep)[-2].startswith('WARNING')

    main.__setattr__('ARGS', _copy_args)


def test_export_with_fetch():
    _val = main.db.REUSE
    main.db.REUSE = True
    _copy_args = copy.deepcopy(main.ARGS)
    main.__setattr__('ARGS', {'credentials': 'USERID|SECRET|REDIRECT_URI'})

    main.fetch(MOCK_SHOW_JSON['media_name'])
    assert main.db.DBConnector().media_exists(MOCK_SHOW_JSON_NAME_NORM)
    main.string_capture.reset()
    main.export(MOCK_SHOW_JSON_NAME_NORM)
    assert not main.string_capture.getvalue().split(os.linesep)[-2].startswith('WARNING')

    main.fetch(MOCK_MOVIE_JSON['media_name'])
    assert main.db.DBConnector().media_exists(MOCK_MOVIE_JSON_NAME_NORM)
    main.string_capture.reset()
    main.export(MOCK_MOVIE_JSON_NAME_NORM)
    assert not main.string_capture.getvalue().split(os.linesep)[-2].startswith('WARNING')

    main.fetch(MOCK_GAME_JSON['media_name'])
    assert main.db.DBConnector().media_exists(MOCK_GAME_JSON_NAME_NORM)
    main.string_capture.reset()
    main.export(MOCK_GAME_JSON_NAME_NORM)
    assert not main.string_capture.getvalue().split(os.linesep)[-2].startswith('WARNING')

    main.__setattr__('ARGS', _copy_args)
    main.db.REUSE = _val


def test_create_playlist():
    _val = main.db.REUSE
    main.db.REUSE = True
    _copy_args = copy.deepcopy(main.ARGS)
    main.__setattr__('ARGS', {'credentials': 'USERID|SECRET|REDIRECT_URI'})

    main.create_playlist(MOCK_SHOW_JSON_NAME_NORM)
    assert main.db.DBConnector().media_exists(MOCK_SHOW_JSON_NAME_NORM)
    main.create_playlist(MOCK_MOVIE_JSON_NAME_NORM)
    assert main.db.DBConnector().media_exists(MOCK_MOVIE_JSON_NAME_NORM)
    main.create_playlist(MOCK_GAME_JSON_NAME_NORM)
    assert main.db.DBConnector().media_exists(MOCK_GAME_JSON_NAME_NORM)

    main.__setattr__('ARGS', _copy_args)
    main.db.REUSE = _val
