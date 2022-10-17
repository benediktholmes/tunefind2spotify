"""Test module for `tunefind2spotify.cmd.main`."""

import pytest
import sys

from tests.cmd import mock_main as main
from tests.cmd.test_actions import MOCK_CRED_FILE_PATH
from tests.test_data.mock_json_data import \
    MOCK_SHOW_JSON,\
    MOCK_MOVIE_JSON,\
    MOCK_GAME_JSON


def test_entrypoint_usage():
    _copy = sys.argv

    sys.argv = ['', '--help']
    with pytest.raises(SystemExit):
        main.entrypoint()

    sys.argv = ['', '--version']
    with pytest.raises(SystemExit):
        main.entrypoint()

    sys.argv = _copy


def test_entrypoint_usage_fetch():
    _copy = sys.argv

    sys.argv = [''] + f'fetch {MOCK_SHOW_JSON["media_name"]}'.split()
    main.entrypoint()

    sys.argv = [''] + f'fetch {MOCK_MOVIE_JSON["media_name"]}'.split()
    main.entrypoint()

    sys.argv = [''] + f'fetch {MOCK_GAME_JSON["media_name"]}'.split()
    main.entrypoint()

    sys.argv = _copy


def test_entrypoint_usage_export_without_fetch():
    _copy = sys.argv

    sys.argv = [''] + f'export {MOCK_SHOW_JSON["media_name"]} -c {MOCK_CRED_FILE_PATH}'.split()
    main.entrypoint()

    sys.argv = [''] + f'export {MOCK_MOVIE_JSON["media_name"]} -c {MOCK_CRED_FILE_PATH}'.split()
    # main.entrypoint()

    sys.argv = [''] + f'export {MOCK_GAME_JSON["media_name"]} -c {MOCK_CRED_FILE_PATH}'.split()
    # main.entrypoint()

    sys.argv = _copy


def test_entrypoint_usage_export_with_fetch():
    _copy = sys.argv

    sys.argv = [''] + f'fetch {MOCK_SHOW_JSON["media_name"]}'.split()
    main.entrypoint()

    sys.argv = [''] + f'export {MOCK_SHOW_JSON["media_name"]} -c {MOCK_CRED_FILE_PATH}'.split()
    main.entrypoint()

    sys.argv = [''] + f'fetch {MOCK_MOVIE_JSON["media_name"]}'.split()
    main.entrypoint()

    sys.argv = [''] + f'export {MOCK_MOVIE_JSON["media_name"]} -c {MOCK_CRED_FILE_PATH}'.split()
    main.entrypoint()

    sys.argv = [''] + f'fetch {MOCK_GAME_JSON["media_name"]}'.split()
    main.entrypoint()

    sys.argv = [''] + f'export {MOCK_GAME_JSON["media_name"]} -c {MOCK_CRED_FILE_PATH}'.split()
    main.entrypoint()

    sys.argv = _copy


def test_entrypoint_usage_pull():
    _copy = sys.argv

    sys.argv = [''] + f'pull {MOCK_SHOW_JSON["media_name"]} -c {MOCK_CRED_FILE_PATH}'.split()
    main.entrypoint()

    sys.argv = [''] + f'pull {MOCK_MOVIE_JSON["media_name"]} -c {MOCK_CRED_FILE_PATH}'.split()
    main.entrypoint()

    sys.argv = [''] + f'pull {MOCK_GAME_JSON["media_name"]} -c {MOCK_CRED_FILE_PATH}'.split()
    main.entrypoint()

    sys.argv = _copy
