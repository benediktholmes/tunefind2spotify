"""Command line interface definition for Tunefind2Spotify.

This module defines and implements the command line interface and usage.

Attributes:
    PROGRAM_NAME (str): Name of this program.
    VERSION_FILE (str): Path to file holding the version number of the program.
    ARGS (dict): Holds the arguments after being processed by argparse.

Todo:
    - Implement correct logging

"""

import argparse
import os

from typing import Optional

from tunefind2spotify.spotify_client import SpotifyClient
from tunefind2spotify.db import DBConnector
from tunefind2spotify import tunefind_scraper
from tunefind2spotify.utils import MediaType

PROGRAM_NAME = 'tunefind2spotify'
VERSION_FILE = os.path.join(
                   os.path.dirname(
                       os.path.dirname(
                           os.path.abspath(__file__)
                       )
                   ),
                   'VERSION'
               )
ARGS = {}


# TODO: Due to hierarchy log which (without secret) and from where credentials where taken!
def find_credentials(delimiter: Optional[str] = '$'):
    """Searches the credentials for the Spotify API passed to the application.

    The following first-match order applies:
    - creds given as parameters
    - creds given as env variables
    - creds in file specified as parameter
    - creds in file with default name

    Args:
        delimiter: Character that separates the credentials in a string.
            Optional, defaults to `$`.

    Returns:
        user, secret, redirect_uri: Credentials used for Spotify's OAuth.

    Raises:
        Exception: In case no credentials were found.
    """
    if 'credentials' in ARGS.keys() and ARGS['credentials'] is not None:
        return ARGS['credentials'].split(delimiter)
    elif 'SPOTIPY_CLIENT_ID' in os.environ.keys() and \
         'SPOTIPY_CLIENT_SECRET' in os.environ.keys() and \
         'SPOTIPY_REDIRECT_URI' in os.environ.keys():
        return os.environ['SPOTIPY_CLIENT_ID'], os.environ['SPOTIPY_CLIENT_SECRET'], os.environ['SPOTIPY_REDIRECT_URI']
    elif 'cred-file' in ARGS.keys():
        path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                ARGS['cred-file'])
        if os.path.isfile(path):
            with open(path, 'r') as f:
                return f.readline().split(delimiter)
        else:
            raise Exception(f'Credentials file {path} not found!')
    else:
        raise Exception('Missing credentials to use Spotify API! Please refer to app\'s'
                        'usage that details the ways how to specify the credentials.')


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
    dbc = DBConnector()
    dbc.insert_json_data(json_data)


def export(media_name: str, **kwargs) -> None:
    """Create playlist for `media_name` from information available in database.

    Args:
        media_name: Name of the media as specified by Tunefind.
    """
    dbc = DBConnector()
    media_type = dbc.get_media_type(media_name)
    if media_type is MediaType.SHOW:
        uris = dbc.get_track_uris_show(media_name=media_name)
    else:
        uris = dbc.get_track_uris_media(media_name=media_name)
    spc = SpotifyClient(*find_credentials())
    spc.export(playlist_name=media_name,
               track_uris=uris,
               description=dbc.get_playlist_description(media_name))


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
                        help='Spotify API credentials specified inline as "ID$SECRET$REDIRECT_URI". Can alternatively '
                             'be specified as via environment variables `SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET` '
                             'and `SPOTIPY_REDIRECT_URI`. Use only one method to specify all credentials. If not '
                             'specified, then credentials are expected to be read from a credentials file.')
    parser.add_argument('-f', '--cred-file',
                        action='store',
                        default='.spotipy_credentials',
                        dest='cred-file',
                        help='Name of file in repository root that specifies Spotify API credentials as '
                             '"ID$SECRET$REDIRECT_URI" in first line of file. If not specified, defaults to file '
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
                              choices=MediaType._member_names_,
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
                              choices=[x.lower() for x in MediaType._member_names_],
                              help='Type of media to scrape. Optional, will be inferred if not given.')

    # TODO: There must be a cleaner way to transfer the string from mt choices to its enum value?
    args = vars(parser.parse_args())
    if 'media_type' in args.keys():
        args.update({'media_type': MediaType.read_in(args['media_type'])})
    # TODO: Log invocation with args
    print(args)
    global ARGS
    ARGS = args

    args['func'](**args)


if __name__ == '__main__':
    entrypoint()