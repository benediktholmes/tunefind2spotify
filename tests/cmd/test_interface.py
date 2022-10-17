"""Test module for external / console script use."""

import os

from tests.cmd.test_actions import MOCK_CRED_FILE_PATH
from tests.test_data.mock_json_data import \
    MOCK_SHOW_JSON,\
    MOCK_MOVIE_JSON,\
    MOCK_GAME_JSON

COMMAND = f'python {os.path.join(os.path.dirname(os.path.abspath(__file__)), "mock_main.py")} ' \
          + '{}'  # -log-level DEBUG


def test_entrypoint_usage():
    os.system(COMMAND.format(f'pull {MOCK_SHOW_JSON["media_name"]} -c {MOCK_CRED_FILE_PATH}'))
    os.system(COMMAND.format(f'pull {MOCK_MOVIE_JSON["media_name"]} -c {MOCK_CRED_FILE_PATH}'))
    os.system(COMMAND.format(f'pull {MOCK_GAME_JSON["media_name"]} -c {MOCK_CRED_FILE_PATH}'))


def test_entrypoint_usage_fetch():
    os.system(COMMAND.format(f'fetch {MOCK_SHOW_JSON["media_name"]}'))
    os.system(COMMAND.format(f'fetch {MOCK_MOVIE_JSON["media_name"]}'))
    os.system(COMMAND.format(f'fetch {MOCK_GAME_JSON["media_name"]}'))


def test_entrypoint_usage_export_without_fetch():
    os.system(COMMAND.format(f'export {MOCK_SHOW_JSON["media_name"]} -c {MOCK_CRED_FILE_PATH}'))
    os.system(COMMAND.format(f'export {MOCK_MOVIE_JSON["media_name"]} -c {MOCK_CRED_FILE_PATH}'))
    os.system(COMMAND.format(f'export {MOCK_GAME_JSON["media_name"]} -c {MOCK_CRED_FILE_PATH}'))


def test_entrypoint_usage_export_with_fetch():
    os.system(COMMAND.format(f'fetch {MOCK_SHOW_JSON["media_name"]}'))
    os.system(COMMAND.format(f'export {MOCK_SHOW_JSON["media_name"]} -c {MOCK_CRED_FILE_PATH}'))

    os.system(COMMAND.format(f'fetch {MOCK_MOVIE_JSON["media_name"]}'))
    os.system(COMMAND.format(f'export {MOCK_MOVIE_JSON["media_name"]} -c {MOCK_CRED_FILE_PATH}'))

    os.system(COMMAND.format(f'fetch {MOCK_GAME_JSON["media_name"]}'))
    os.system(COMMAND.format(f'export {MOCK_GAME_JSON["media_name"]} -c {MOCK_CRED_FILE_PATH}'))


def test_entrypoint_usage_pull():
    os.system(COMMAND.format(f'pull {MOCK_SHOW_JSON["media_name"]} -c {MOCK_CRED_FILE_PATH}'))
    os.system(COMMAND.format(f'pull {MOCK_MOVIE_JSON["media_name"]} -c {MOCK_CRED_FILE_PATH}'))
    os.system(COMMAND.format(f'pull {MOCK_GAME_JSON["media_name"]} -c {MOCK_CRED_FILE_PATH}'))
