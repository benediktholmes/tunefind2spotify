"""Command line interface definition for Tunefind2Spotify.

This module defines and implements the command line interface and usage.

Attributes:
    PROGRAM_NAME (str): Name of this program.
    VERSION_FILE (str): Path to file holding the version number of the program.
    ARGS (dict): Holds the arguments after being processed by argparse.
"""

import argparse
import os

from typing import Optional

from tunefind2spotify import tunefind_scraper
from tunefind2spotify import db
from tunefind2spotify.exceptions import log_and_raise, MissingCredentialsException
from tunefind2spotify.log import fetch_logger
from tunefind2spotify.spotify_client import SpotifyClient
from tunefind2spotify.utils import EnumAction, MediaType


logger = fetch_logger(__name__)

PROGRAM_NAME = 'tunefind2spotify'
VERSION_FILE = os.path.join(
                   os.path.dirname(
                       os.path.dirname(
                           os.path.abspath(__file__)
                       )
                   ),
                   'VERSION'
               )
DEFAULT_CRED_FILE = '.spotipy_credentials'
ARGS = {}


def find_credentials(delimiter: Optional[str] = '|'):
    """Searches the credentials for the Spotify API passed to the application.

    The following first-match order applies:
    - creds given as parameters
    - creds given as env variables
    - creds in file specified as parameter
    - creds in file with default name

    Args:
        delimiter: Character that separates the credentials in a string.
            Optional, defaults to `|`.

    Returns:
        user, secret, redirect_uri: Credentials used for Spotify's OAuth.

    Raises:
        ValueError: In case credentials do not fit format, the delimiter does
            not obey its restrictions or the path to given file does not exist.
        MissingCredentialsException: In case no credentials were found.
    """
    def _unpack(creds: str) -> (str, str, str):
        if str.count(creds, delimiter) != 2 or len(creds) < 5:
            log_and_raise(logger, ValueError, f'Insufficient credentials to be extraced from \'{creds}\'.')
        return creds.split(delimiter)

    if len(delimiter) != 1:
        log_and_raise(logger, ValueError, f'Delimiter must be a single character. Provided \'{delimiter}\' instead.')

    if 'credentials' in ARGS.keys() and ARGS['credentials'] is not None:
        logger.info('Spotipy credentials taken from cmd arguments.')
        i, s, r = _unpack(ARGS['credentials'])
        logger.debug(f'Using Spotify Client ID: \'{i}\'.')
        return i, s, r
    elif 'SPOTIPY_CLIENT_ID' in os.environ.keys() and \
         'SPOTIPY_CLIENT_SECRET' in os.environ.keys() and \
         'SPOTIPY_REDIRECT_URI' in os.environ.keys():
        logger.debug('Spotipy credentials taken from env variables.')
        logger.debug(f'Using Spotify Client ID: \'{os.environ["SPOTIPY_CLIENT_ID"]}\'.')
        return os.environ['SPOTIPY_CLIENT_ID'], os.environ['SPOTIPY_CLIENT_SECRET'], os.environ['SPOTIPY_REDIRECT_URI']
    elif 'cred-file' in ARGS.keys():
        path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                ARGS['cred-file'])
        if os.path.isfile(path):
            with open(path, 'r') as f:
                logger.debug(f'Spotipy credentials taken from file \'{path}\'.')
                i, s, r = _unpack(f.readline())
                logger.debug(f'Using Spotify Client ID: \'{i}\'.')
                return i, s, r
        else:
            log_and_raise(logger, ValueError, f'Credentials file {path} not found!')
    else:
        log_and_raise(logger, MissingCredentialsException,
                      'No credentials found to be used with Spotify API! Please '
                      'refer to app\'s usage that details the ways how to '
                      'specify the credentials.')


def fetch(media_name: str, media_type: Optional[MediaType] = None, **kwargs) -> None:
    """Scrapes song info for `media_name` from Tunefind and stores in database.

    Note:
        If the media on Tunefind is specified by an url such as:

            https://www.tunefind.com/game/assassins-creed-valhalla-2020

        then the corresponding media name is `assassins-creed-valhalla-2020`
        and the media type `game` respectively.

    Args:
        media_name: Name of the media as specified by Tunefind.
        media_type: Type of media as in the categories found on Tunefind. Must
            be one of `MediaType` enum values. Optional, defaults to `None` in
            which case the correct media type will be inferred from probing Tunefind.
    """
    json_data = tunefind_scraper.scrape(media_name=media_name, media_type=media_type)
    dbc = db.DBConnector()
    dbc.insert_json_data(json_data)


def export(media_name: str, **kwargs) -> None:
    """Create playlist for `media_name` from information available in database.

    Args:
        media_name: Name of the media as specified by Tunefind.
    """
    media_name = tunefind_scraper.name_normalization(media_name)
    dbc = db.DBConnector()
    if dbc.media_exists(media_name):
        media_type = dbc.get_media_type(media_name)
        if media_type is MediaType.SHOW:
            uris = dbc.get_track_uris_show(media_name=media_name)
        else:
            uris = dbc.get_track_uris_media(media_name=media_name)
        spc = SpotifyClient(*find_credentials())
        spc.export(playlist_name=dbc.get_readable_name(media_name),
                   track_uris=uris,
                   description=dbc.get_playlist_description(media_name))
    else:
        logger.warning(f'Media \'{media_name}\' does not exist in database. Please fetch first.')


def create_playlist(media_name: str, media_type: Optional[MediaType] = None, **kwargs) -> None:
    """Fetches then exports the data for given `media_name`.

    Args:
        media_name: Name of the media as specified by Tunefind.
        media_type: Type of media as in the categories found on Tunefind. Must
            be one of `MediaType` enum values. Optional, defaults to `None` in
            which case the correct media type will be inferred from probing Tunefind.
    """
    fetch(media_name, media_type)
    export(media_name)


def entrypoint():
    parser = argparse.ArgumentParser(prog=PROGRAM_NAME,
                                     description='Scrape data from Tunefind to create Spotify playlists')

    parser.add_argument('-v', '--version',
                        action='version',
                        version=f'{PROGRAM_NAME} {open(VERSION_FILE, "r").readline()}')
    parser.add_argument('-c', '--credentials',
                        action='store',
                        help='Spotify API credentials specified inline as "ID|SECRET|REDIRECT_URI". Can alternatively '
                             'be specified as via environment variables `SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET` '
                             'and `SPOTIPY_REDIRECT_URI`. Use only one method to specify all credentials. If not '
                             'specified, then credentials are expected to be read from a credentials file.')
    parser.add_argument('-f', '--cred-file',
                        action='store',
                        default=DEFAULT_CRED_FILE,
                        dest='cred-file',
                        help='Name of file in repository root that specifies Spotify API credentials as '
                             '"ID|SECRET|REDIRECT_URI" in first line of file. If not specified, defaults to file '
                             '`.spotipy-credentials`')

    # create the subparsers
    subparsers = parser.add_subparsers(help='sub-command help')

    # fetch command
    parser_fetch = subparsers.add_parser('fetch',
                                         help='Scrape song info for media from Tunefind and store in database.')
    parser_fetch.set_defaults(func=fetch)
    parser_fetch.add_argument('-mn', '--media_name',
                              type=str,
                              required=True,
                              help='Name of media to scrape.')
    parser_fetch.add_argument('-mt', '--media_type',
                              type=MediaType,
                              action=EnumAction,
                              help='Type of media to scrape. Optional, will be inferred if not given.')
    # export command
    parser_fetch = subparsers.add_parser('export',
                                         help='Create playlist from media information in database.')
    parser_fetch.set_defaults(func=export)
    parser_fetch.add_argument('-mn', '--media_name',
                              type=str, required=True,
                              help='Name of media to scrape.')

    # create_playlist command
    parser_fetch = subparsers.add_parser('create_playlist',
                                         help='Combination of first fetch and then export.')
    parser_fetch.set_defaults(func=create_playlist)
    parser_fetch.add_argument('-mn', '--media_name',
                              type=str,
                              required=True,
                              help='Name of media to scrape.')
    parser_fetch.add_argument('-mt', '--media_type',
                              type=MediaType,
                              action=EnumAction,
                              help='Type of media to scrape. Optional, will be inferred if not given.')

    args = vars(parser.parse_args())
    logger.debug(f'Application was invoked with args: {args}.')
    global ARGS
    ARGS = args

    logger.info(f'Invocation of {args["func"].__name__} function.')
    args['func'](**args)


if __name__ == '__main__':
    logger.debug('Commandline invocation started.')
    entrypoint()
    logger.debug('Done.')
