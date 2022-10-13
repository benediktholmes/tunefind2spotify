"""Module that defines top-level API for end-user."""

from typing import Optional

from tunefind2spotify.core import tunefind_scraper, db
from tunefind2spotify.log import fetch_logger
from tunefind2spotify.core.spotify_client import SpotifyClient, SpotifyCredentials
from tunefind2spotify.utils import MediaType


logger = fetch_logger(__name__)


def fetch(media_name: str,
          media_type: Optional[MediaType] = None,
          **kwargs) -> None:
    """Scrapes song info for `media_name` from Tunefind and stores in database.

    Note:
        If the media on Tunefind is specified by an url such as:

            https://www.tunefind.com/game/assassins-creed-valhalla-2020

        then the corresponding media name is `'assassins-creed-valhalla-2020'`
        and the media type `MediaType.GAME` respectively.

    Args:
        media_name: Name of the media as specified by Tunefind.
        media_type: Type of media as in the categories found on Tunefind. Must
            be one of `MediaType` enum values. Optional, defaults to `None` in
            which case the correct media type will be inferred from probing Tunefind.
    """
    media_name, media_type = tunefind_scraper.name_and_type_check(media_name, media_type)
    json_data = tunefind_scraper.scrape(media_name=media_name, media_type=media_type)
    dbc = db.DBConnector()
    dbc.insert_json_data(json_data)


def export(media_name: str,
           credentials: SpotifyCredentials,
           **kwargs) -> None:
    """Create playlist for `media_name` from information available in database.

    Args:
        media_name: Name of the media as specified by Tunefind.
        credentials: Spotify API credentials dataclass.
    """
    media_name = tunefind_scraper.name_normalization(media_name)
    dbc = db.DBConnector()
    if dbc.media_exists(media_name):
        media_type = dbc.get_media_type(media_name)
        if media_type is MediaType.SHOW:
            uris = dbc.get_track_uris_show(media_name=media_name)
        else:
            uris = dbc.get_track_uris_media(media_name=media_name)
        spc = SpotifyClient(credentials)
        spc.export(playlist_name=dbc.get_readable_name(media_name),
                   track_uris=uris,
                   description=dbc.get_playlist_description(media_name))
    else:
        logger.warning(f'Media \'{media_name}\' does not exist in database. Please fetch first.')


def create_playlist(media_name: str,
                    credentials: SpotifyCredentials,
                    media_type: Optional[MediaType] = None,
                    **kwargs) -> None:
    """Fetches then exports the data for given `media_name`.

    Args:
        media_name: Name of the media as specified by Tunefind.
        credentials: Spotify API credentials dataclass.
        media_type: Type of media as in the categories found on Tunefind. Must
            be one of `MediaType` enum values. Optional, defaults to `None` in
            which case the correct media type will be inferred from probing Tunefind.
    """
    fetch(media_name, media_type)
    export(media_name, credentials)
