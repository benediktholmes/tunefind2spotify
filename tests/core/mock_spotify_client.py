"""Mock of module `tunefind2spotify.core.spotify_client`.

To be used as surrogate for above mentioned module during testing.

Monkey patches the object initialization for
`tunefind2spotify.core.spotify_client.SpotifyClient` that replaces the original
client object (`spotipy.client.Spotify`) attribute with a mock that replaces(?)
Spotify API calls with noops and returns correct information using sample data
@ `tests.test_data.mock_json_data`. Prevents that real playlists are created
during testing. Implies that successful tests are only valid while the `spotipy`
API does not change.

The module logger is also monkey patched with a logger that writes into a
`StringIO` object. For testing purposes, logged content can be read from
`*module*.string_capture`.

Via module-level `__getattr__` the (remaining) namespace of the mocked module is
made available to the importer of the module.
"""

from tunefind2spotify.core import spotify_client

from tests.mock_logger import mock_logger
from tests.test_data.mock_json_data import \
    MOCK_SHOW_JSON, \
    MOCK_MOVIE_JSON, \
    MOCK_GAME_JSON, \
    _get_show_uris


class MockSpotifyClient:
    """Mock object for SpotifyClient that mocks returning methods, yields a
       noop function for any other attribute requested and counts calls to
       returned methods.
    """
    def __init__(self):
        self._counter = {}
        # some fake playlists
        self._crt_playlists = {'items': [{'name': 'DOESNOTEXIST', 'id': 00},
                                         {'name': 'DOESNTEXIST2', 'id': 99}]}

    def __getattribute__(self, item):  # noqa: C901
        if item in ['_counter', '_crt_playlists', 'increment', 'reset_counter']:
            return object.__getattribute__(self, item)
        if item == 'current_user_playlists':
            def func(limit=1, offset=0, *args, **kwargs):
                self.increment(item)
                # force to unify all test cases and hit all branches
                limit = 1
                offset //= 50
                return {'items': self._crt_playlists['items'][offset:limit + offset]}
        elif item == 'user_playlist_create':
            def func(id_, pn, *args, **kwargs):
                self.increment(item)
                pid = {MOCK_SHOW_JSON['media_name']: 12,
                       MOCK_MOVIE_JSON['media_name']: 34,
                       MOCK_GAME_JSON['media_name']: 56}[pn]
                self._crt_playlists['items'].append({'name': pn, 'id': pid})
                return {'id': pid}
        elif item == 'playlist_items':
            def func(pid, limit=1, offset=0, *args, **kwargs):
                # force to unify all test cases and hit all branches
                limit = 1
                offset //= 50
                self.increment(item)
                return {12: {'items': [{'track': {'uri': x}}
                                       for x in _get_show_uris()][offset:limit + offset]},
                        34: {'items': [{'track': {'uri': x['spotify']}}
                                       for x in MOCK_MOVIE_JSON['songs']][offset:limit + offset]},
                        56: {'items': [{'track': {'uri': x['spotify']}}
                                       for x in MOCK_GAME_JSON['songs']][offset:limit + offset]}
                        }[pid]
        elif item == 'me':
            def func(*args, **kwargs):
                self.increment(item)
                return {'id': 0}
        else:
            def func(*args, **kwargs):
                self.increment(item)
        return func

    def increment(self, name):
        if name not in self._counter.keys():
            self._counter[name] = 0
        self._counter[name] += 1

    def reset_counter(self):
        self._counter = dict()


def mock_init_spc(self, *args, **kwargs):
    # monkey patch the client object with mock instance
    self.client = MockSpotifyClient()


# monkey patch module
logger, string_capture = mock_logger(__name__)
spotify_client.logger = logger
spotify_client.string_capture = string_capture
spotify_client.SpotifyClient.__init__ = mock_init_spc


def __getattr__(name):
    return getattr(spotify_client, name)


def __setattr__(name, value):
    setattr(spotify_client, name, value)


def test_mock_object():
    spc = spotify_client.SpotifyClient()
    assert isinstance(spc.client, MockSpotifyClient)
    # test mock functions
    spc.client.current_user_playlists()
    playlist = spc.client.user_playlist_create(0, MOCK_SHOW_JSON['media_name'])
    pid = playlist['id']
    items = spc.client.playlist_items(pid)
    assert items, f'Items should be non-empty list of playlist items for mock show. Instead got : {items} .'
    playlist = spc.client.user_playlist_create(0, MOCK_MOVIE_JSON['media_name'])
    pid = playlist['id']
    items = spc.client.playlist_items(pid)
    assert items, f'Items should be non-empty list of playlist items for mock movie. Instead got : {items} .'
    playlist = spc.client.user_playlist_create(0, MOCK_GAME_JSON['media_name'])
    pid = playlist['id']
    items = spc.client.playlist_items(pid)
    assert items, f'Items should be non-empty list of playlist items for mock game. Instead got : {items} .'
    # test non-existent mock functions
    assert callable(spc.client.nonexistentfunction), \
        'MockSpotifyClient\'s `__getattribute__` should always return a function object! ' \
        f'Instead got: {spc.client.nonexistentfunction} .'
    spc.client.nonexistentfunction()
    # check functions are counted correctly
    assert spc.client._counter['current_user_playlists'] == 1, \
        'Method \'current_user_playlists\' was called 1 times, ' \
        f'but {spc.client._counter["current_user_playlists"]} calls were recorded!'
    assert spc.client._counter['user_playlist_create'] == 3, \
        'Method \'user_playlist_create\' was called 3 times, ' \
        f'but {spc.client._counter["user_playlist_create"]} calls were recorded!'
    assert spc.client._counter['playlist_items'] == 3, \
        'Method \'playlist_items\' was called 3 times, ' \
        f'but {spc.client._counter["playlist_items"]} calls were recorded!'
    assert spc.client._counter['nonexistentfunction'] == 1, \
        'Method \'nonexistentfunction\' was called 1 times, ' \
        f'but {spc.client._counter["nonexistentfunction"]} calls were recorded!'
    # test reset
    spc.client.reset_counter()
    assert not spc.client._counter, f'Counter should be empty dict after reset, instead got: {spc.client._counter} .'
