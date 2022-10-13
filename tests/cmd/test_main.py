"""Test module for `tunefind2spotify.cmd.main`."""

import os
import pytest
import sys

from tests.cmd import mock_main as main
from tests.test_data.mock_json_data import \
    MOCK_SHOW_JSON,\
    MOCK_MOVIE_JSON,\
    MOCK_GAME_JSON


COMMAND = f'PYTHONPATH={os.path.dirname(os.path.dirname(os.path.abspath(__file__)))} ' + \
          f'python {os.path.join("tests", "mock_main.py")} ' + \
          '{}'


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

    sys.argv = [''] + f'export {MOCK_SHOW_JSON["media_name"]}'.split()
    main.entrypoint()

    sys.argv = [''] + f'export {MOCK_MOVIE_JSON["media_name"]}'.split()
    main.entrypoint()

    sys.argv = [''] + f'export {MOCK_GAME_JSON["media_name"]}'.split()
    main.entrypoint()

    sys.argv = _copy


def test_entrypoint_usage_export_with_fetch():
    _copy = sys.argv

    sys.argv = [''] + f'fetch {MOCK_SHOW_JSON["media_name"]}'.split()
    main.entrypoint()

    sys.argv = [''] + f'export {MOCK_SHOW_JSON["media_name"]}'.split()
    main.entrypoint()

    sys.argv = [''] + f'fetch {MOCK_MOVIE_JSON["media_name"]}'.split()
    main.entrypoint()

    sys.argv = [''] + f'export {MOCK_MOVIE_JSON["media_name"]}'.split()
    main.entrypoint()

    sys.argv = [''] + f'fetch {MOCK_GAME_JSON["media_name"]}'.split()
    main.entrypoint()

    sys.argv = [''] + f'export {MOCK_GAME_JSON["media_name"]}'.split()
    main.entrypoint()

    sys.argv = _copy


def test_entrypoint_usage_create_playlist():
    _copy = sys.argv

    sys.argv = [''] + f'create_playlist {MOCK_SHOW_JSON["media_name"]}'.split()
    main.entrypoint()

    sys.argv = [''] + f'create_playlist {MOCK_MOVIE_JSON["media_name"]}'.split()
    main.entrypoint()

    sys.argv = [''] + f'create_playlist {MOCK_GAME_JSON["media_name"]}'.split()
    main.entrypoint()

    sys.argv = _copy