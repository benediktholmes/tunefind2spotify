"""Test module for `tunefind2spotify.cmd.actions`."""

import os
import pytest

from tunefind2spotify.cmd import actions

from tests.mock_logger import mock_logger

logger, string_capture = mock_logger(__name__)
actions.logger = logger
actions.string_capture = string_capture


USERID = 'USERIDx0123456789012345678901234'
SECRET = 'SECRETx0123456789012345678901234'
REDIRECT_URI = 'https://REDIRECT_URI'

MOCK_CRED_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                   'test_data',
                                   'mock_credentials'
                                   )


def _assert(x):
    assert x.client_id == USERID
    assert x.client_secret == SECRET
    assert x.redirect_uri == REDIRECT_URI


def test_find_credentials_delimiter():
    with pytest.raises(ValueError):
        actions.find_credentials('', delimiter='')
    with pytest.raises(ValueError):
        actions.find_credentials('', delimiter='ABC')


def test_find_credentials_in_params():
    sc = actions.find_credentials(f'{USERID}|{SECRET}|{REDIRECT_URI}')
    _assert(sc)


def test_find_credentials_in_env():
    os.environ['SPOTIPY_CLIENT_ID'] = USERID
    os.environ['SPOTIPY_CLIENT_SECRET'] = SECRET
    os.environ['SPOTIPY_REDIRECT_URI'] = REDIRECT_URI
    sc = actions.find_credentials('')
    _assert(sc)
    del os.environ['SPOTIPY_CLIENT_ID']
    del os.environ['SPOTIPY_CLIENT_SECRET']
    del os.environ['SPOTIPY_REDIRECT_URI']


def test_find_credentials_in_file_specified():
    sc = actions.find_credentials(MOCK_CRED_FILE_PATH)
    _assert(sc)


def test_find_credentials_not_found():
    with pytest.raises(actions.MissingCredentialsException):
        actions.find_credentials('')
    with pytest.raises(actions.MissingCredentialsException):
        actions.find_credentials('ABC')
