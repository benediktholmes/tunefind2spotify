"""Interface to Spotify API.

This modules defines a class that, utilizing `spotipy`, exposes customized
functionality for creating and modifying playlists on Spotify.

To authenticate against Spotify, register a new app at
`https://developer.spotify.com/dashboard/`. Client id and client secret are
shown immediately. A redirect URI can be added by editing the information on the
app in the developer dashboard. These three parts of credentials must be used to
authenticate the client class against Spotify. At first usage, the client must
be authenticated manually via the redirect URI. Afterwards, the access token is
refreshed automatically and cached in `PROJECT_DIR/.cache`.

"""

from typing import List, Optional

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from tqdm import tqdm

from tunefind2spotify.log import fetch_logger
from tunefind2spotify.utils import singleton


logger = fetch_logger(__name__)


# TODO: Error handling if playlist_add_items handles 40X return code!
@singleton
class SpotifyClient:
    """Client that exposes relevant interface to Spotify.

    Attributes:
        client (spotipy.client.Spotify): Spotipy client object.
    """

    def __init__(self,
                 client_id: str,
                 client_secret: str,
                 redirect_uri: str) -> None:
        """Initializes the Spotify client with authentication data.

        Args:
            client_id: ID of registered app.
            client_secret: Secret of registered app.
            redirect_uri: Redirect URI specified for registered app.
        """
        self.client = Spotify(oauth_manager=SpotifyOAuth(
                    client_id=client_id,
                    client_secret=client_secret,
                    redirect_uri=redirect_uri,
                    scope=['playlist-modify-private']
                )
        )
        logger.debug(f'Spotify client {self} successfully initialized and authenticated.')

    # TODO: In future differentiate media_name & playlist_name.
    # TODO: Ensure to only add unique URIs!
    def export(self,
               playlist_name: str,
               track_uris: List[str],
               description: Optional[str] = '') -> str:
        """Creates new public playlist with given name and songlist.

        Args:
            playlist_name: Name of the playlist to be created.
            track_uris: List of URIs to songs to be added to new playlist.
            description: Description of playlist to be displayed on Spotify.
                Optional, defaults to empty string.


        Returns:
            ID of newly created playlist
        """
        logger.info(f'Exporting playlist \'{playlist_name}\' to Spotify ...')
        # create playlist
        if not self._playlist_exists(playlist_name):
            playlist = self.client.user_playlist_create(self.client.me()['id'],
                                                        playlist_name,
                                                        public=False,
                                                        collaborative=False,
                                                        description='')
            playlist_id = playlist['id']
            self.client.playlist_change_details(playlist_id,
                                                playlist_name,
                                                public=False,
                                                collaborative=False,
                                                description=description)
            logger.info(f'Created new playlist: \'{playlist_name}\' ({playlist_id})')
            # batch fill playlist
            for batch_idx in tqdm(range(len(track_uris) // 50 + 1), disable=False):
                batch = track_uris[50 * batch_idx:50 * (batch_idx + 1)]
                for track_uri in batch:
                    logger.debug(f'Adding track \'{track_uri}\' to playlist \'{playlist_name}\' ({playlist_id})')
                self.client.playlist_add_items(playlist_id, batch)
        else:
            playlist_id = self._get_playlist_id(playlist_name)
            logger.info(f'Playlist \'{playlist_name}\' ({playlist_id}) exists. Updating ...')
            self.client.playlist_change_details(playlist_id,
                                                playlist_name,
                                                public=False,
                                                collaborative=False,
                                                description=description)

            # single fill playlist with checks
            for track_uri in tqdm(track_uris, disable=False):
                if not self._item_exists_in_playlist(playlist_id, track_uri):
                    logger.debug(f'Adding track \'{track_uri}\' to playlist \'{playlist_name}\' ({playlist_id})')
                    self.client.playlist_add_items(playlist_id, [track_uri])
                else:
                    logger.debug(f'Track \'{track_uri}\' already exists in \'{playlist_name}\' ({playlist_id})')

        return playlist_id

    def _playlist_exists(self, name: str) -> bool:
        limit, offset = 50, 0
        while playlists := self.client.current_user_playlists(limit, offset)['items']:
            if name in [x['name'] for x in playlists]:
                return True
            offset += limit
        return False

    def _get_playlist_id(self, name: str) -> str:
        limit, offset = 50, 0
        while playlists := self.client.current_user_playlists(limit, offset)['items']:
            for x in playlists:
                if name == x['name']:
                    return x['id']
            offset += limit
        return ''

    def _item_exists_in_playlist(self,
                                 playlist_id: str,
                                 track_uri: str) -> bool:
        limit, offset = 50, 0
        while items := self.client.playlist_items(playlist_id, limit=limit, offset=offset)['items']:
            if track_uri in [x['track']['uri'] for x in items]:
                return True
            offset += limit
        return False
