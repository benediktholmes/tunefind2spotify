"""Command line interface definition for Tunefind2Spotify.

This module defines and implements the command line interface and usage.

Attributes:
    PROGRAM_NAME (str): Name of this program.
    VERSION_FILE (str): Path to file holding the version number of the program.
    DEFAULT_CRED_FILE (str): Default file to read Spotify API credentials from.
"""

import argparse
import os
import sys

_TOP_LEVEL_PATH = os.path.dirname(
                       os.path.dirname(
                           os.path.dirname(
                               os.path.abspath(__file__)
                           )
                       )
                   )
sys.path.insert(0, _TOP_LEVEL_PATH)

from tunefind2spotify import api  # noqa: E402
from tunefind2spotify.cmd.actions import EnumAction, SpotifyCredentialsAction  # noqa: E402
from tunefind2spotify.log import fetch_logger  # noqa: E402
from tunefind2spotify.utils import MediaType  # noqa: E402

logger = fetch_logger(__name__)

PROGRAM_NAME = 'tunefind2spotify'
VERSION_FILE = os.path.join(_TOP_LEVEL_PATH, 'VERSION')
DEFAULT_CRED_FILE = '.spotipy_credentials'


def entrypoint():
    parser = argparse.ArgumentParser(prog=PROGRAM_NAME,
                                     description='Scrape data from Tunefind to create Spotify playlists')

    parser.add_argument('-v', '--version',
                        action='version',
                        version=f'{PROGRAM_NAME} {open(VERSION_FILE, "r").readline()}')

    credentials_options = (['-c', '--credentials'],
                           dict(dest='credentials',
                                type=str,
                                default=DEFAULT_CRED_FILE,
                                action=SpotifyCredentialsAction,
                                help='Spotify API credentials to be either specified inline or via path to a '
                                     'credentials file, whose first line includes credentials. In either case '
                                     'credentials are expected in the format "ID|SECRET|REDIRECT_URI". '
                                     'Alternatively specifying credentials via environment variables '
                                     '`SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET` and `SPOTIPY_REDIRECT_URI` takes '
                                     'precedence. '
                                     'If none of the above are specified, credentials are by default expected in '
                                     'file `{DEFAULT_CRED_FILE}`.')
                           )

    # create the subparsers
    subparsers = parser.add_subparsers(help='sub-command help')

    # fetch command
    parser_fetch = subparsers.add_parser('fetch',
                                         help='Scrape song info for media from Tunefind and store in database.')
    parser_fetch.set_defaults(func=api.fetch)
    parser_fetch.add_argument('media_name',
                              metavar='MEDIA-NAME',
                              type=str,
                              help='Name of media to scrape.')
    parser_fetch.add_argument('-mt', '--media_type',
                              dest='media_type',
                              type=MediaType,
                              action=EnumAction,
                              help='Type of media to scrape. Optional, will be inferred if not given.')

    # export command
    parser_export = subparsers.add_parser('export',
                                          help='Create playlist from media information in database.')
    parser_export.set_defaults(func=api.export)
    parser_export.add_argument('media_name',
                               metavar='MEDIA-NAME',
                               type=str,
                               help='Name of media to scrape.')
    cred_arg = parser_export.add_argument(*credentials_options[0], **credentials_options[1])

    # create_playlist command
    parser_create_playlist = subparsers.add_parser('create_playlist',
                                                   help='Combination of first fetch and then export.')
    parser_create_playlist.set_defaults(func=api.create_playlist)
    parser_create_playlist.add_argument('media_name',
                                        metavar='MEDIA-NAME',
                                        type=str,
                                        help='Name of media to scrape.')
    cred_arg = parser_create_playlist.add_argument(*credentials_options[0], **credentials_options[1])
    parser_create_playlist.add_argument('-mt', '--media_type',
                                        type=MediaType,
                                        action=EnumAction,
                                        help='Type of media to scrape. Optional, will be inferred if not given.')

    args = parser.parse_args()
    if credentials_options[1]['dest'] in vars(args).keys():
        # Invoke SpotifyCredentialsAction manually in case default was read
        if vars(args)[cred_arg.dest] == cred_arg.default:
            logger.debug('Invoking SpotifyCredentialsAction manually to handle default value.')
            cred_arg(parser, args, cred_arg.default)
    else:
        logger.debug('Skipping SpotifyCredentialsAction.')
    args = vars(args)
    logger.debug(f'Application was invoked with args: {args}.')
    logger.info(f'Invocation of {args["func"].__name__} function.')
    args['func'](**args)


if __name__ == '__main__':
    logger.debug('Commandline invocation started.')
    entrypoint()
    logger.debug('Done.')
