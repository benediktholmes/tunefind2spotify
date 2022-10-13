"""Definition of custom `argparse.Action` derivatives for use with cmd API."""

import argparse
import enum
import os

from typing import Optional

from tunefind2spotify.core.spotify_client import SpotifyCredentials
from tunefind2spotify.exceptions import log_and_raise, MissingCredentialsException
from tunefind2spotify.log import fetch_logger

logger = fetch_logger(__name__)


def _unpack(creds: str, delimiter: str) -> SpotifyCredentials:
    """Attempts to extract credential parts from given string.

    Args:
        creds: String that holds credentials.
        delimiter: Character that separates credentials in `creds`.

    Returns:
        Spotify API credentials dataclass.
    """
    i, s, r = '', '', ''
    if str.count(creds, delimiter) != 2 or len(creds) < 5:
        logger.debug(f'Insufficient credentials to be extracted from string \'{creds}\'.')
    else:
        i, s, r = creds.split(delimiter)
    return SpotifyCredentials(i, s, r)


def find_credentials(args: dict, delimiter: Optional[str] = '|') -> SpotifyCredentials:
    """Searches the credentials for the Spotify API passed to the application.

    Note:
        The following first-match order applies:
        1. creds given as env variables
        2. creds given as inline argument
        3. creds in file specified as argument

    Args:
        args: Dictionary of namespace object returned from argparse parser.
        delimiter: Character that separates the credentials in a string.
            Optional, defaults to `|`.

    Returns:
        Credentials dataclass used for Spotify's OAuth.

    Raises:
        ValueError: In case env variable credentials do not fit valid format
            determined by `SpotifyCredentials.is_valid`.
        MissingCredentialsException: In case no credentials with valid format
            were found.
    """

    if len(delimiter) != 1:
        log_and_raise(logger, ValueError, f'Delimiter must be a single character. Provided \'{delimiter}\' instead.')

    if 'SPOTIPY_CLIENT_ID' in os.environ.keys() and \
            'SPOTIPY_CLIENT_SECRET' in os.environ.keys() and \
            'SPOTIPY_REDIRECT_URI' in os.environ.keys():
        sc = SpotifyCredentials(os.environ['SPOTIPY_CLIENT_ID'],
                                os.environ['SPOTIPY_CLIENT_SECRET'],
                                os.environ['SPOTIPY_REDIRECT_URI'])
        logger.debug('Spotipy credentials taken from env variables.')
        logger.debug(f'Using Spotify Client Credentials: {sc}.')
        if sc.is_valid():
            return sc
        else:
            log_and_raise(logger, ValueError, 'Credentials passed as env variables are not of valid format!')
    elif 'credentials' in args.keys() and args['credentials'] is not None:
        logger.debug('Credentials not passed via env variables. '
                     'Continuing to interpret argument as inline credentials.')
        sc = _unpack(args['credentials'], delimiter)
        if sc.is_valid():
            logger.info('Spotipy credentials taken from inline arguments.')
            logger.debug(f'Using Spotify Client Credentials: {sc}.')
            return sc
        else:
            logger.debug('Inline credentials not of valid format. Continuing to interpret argument as file path.')
            path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                    args['credentials'])
            if os.path.isfile(path):
                with open(path, 'r') as f:
                    sc = _unpack(f.readline(), delimiter)
                    if sc.is_valid():
                        logger.debug(f'Spotipy credentials taken from file \'{path}\'.')
                        logger.debug(f'Using Spotify Client Credentials: {sc}.')
                        return sc
                    else:
                        log_and_raise(logger, ValueError,
                                      f'Input is interpreted as file path yet the content of first line of `{path}` '
                                      'are not valid credentials!')
            else:
                log_and_raise(logger, MissingCredentialsException,
                              'No credentials found to be used with Spotify API! Please refer to app\'s usage that '
                              'details the ways how to specify the credentials.')
    else:
        log_and_raise(logger, MissingCredentialsException,
                      'Credentials neither passed via env variables nor is '
                      '\'credentials\' a (not None valued) key in passed dictionary.')


class EnumAction(argparse.Action):
    """Argparse action for handling enum conversion."""

    def __init__(self, **kwargs) -> None:
        """Sets type of choices."""
        enum_type = kwargs.pop('type', None)
        if enum_type is None:
            raise ValueError(f'Argument `{type}` must be assigned an enum when using EnumAction')
        if not issubclass(enum_type, enum.Enum):
            raise TypeError(f'Argument `{type}` must be an enum when using EnumAction')

        kwargs.setdefault('choices', tuple(e.name for e in enum_type))

        super(EnumAction, self).__init__(**kwargs)
        self._enum = enum_type

    def __call__(self,
                 parser,
                 namespace,
                 values,
                 option_string=None) -> None:
        """Convert value to enum."""
        value = self._enum[values]
        setattr(namespace, self.dest, value)


class SpotifyCredentialsAction(argparse.Action):
    """Argparse action for handling Spotify credentials."""

    def __call__(self,
                 parser,
                 namespace,
                 values,
                 option_string=None) -> None:
        """Find and set Spotify credentials."""
        value = find_credentials(vars(namespace))
        setattr(namespace, self.dest, value)
