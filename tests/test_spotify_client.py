from tests.mock_spotify_client import SpotifyClient
from tests.test_data.mock_json_data import \
    MOCK_SHOW_JSON, \
    MOCK_MOVIE_JSON, \
    MOCK_GAME_JSON, \
    MOCK_SHOW_JSON_NAME_NORM, \
    MOCK_MOVIE_JSON_NAME_NORM, \
    MOCK_GAME_JSON_NAME_NORM, \
    _get_show_uris


def test_export_new_show():
    spc = SpotifyClient()
    assert not MOCK_SHOW_JSON['media_name'] in [x['name'] for x in spc.client._crt_playlists['items']], \
        f'Initially _crt_playlists should not contain show empty!' \
        f'Instead got: {spc.client.current_user_playlists()["items"]} .'
    uris_show = _get_show_uris()
    spc.client.reset_counter()
    spc.export(playlist_name=MOCK_SHOW_JSON_NAME_NORM,
               track_uris=uris_show,
               description='')
    assert spc.client._counter['current_user_playlists'] == 3, \
        f'Expected 3 call(s) to \'current_user_playlists\' ! ' \
        f'Instead got {spc.client._counter["current_user_playlists"]} calls.'
    assert spc.client._counter['me'] == 1, \
        f'Expected 1 call(s) to \'me\' ! ' \
        f'Instead got {spc.client._counter["me"]} calls.'
    assert spc.client._counter['user_playlist_create'] == 1, \
        f'Expected 1 call(s) to \'user_playlist_create\' ! ' \
        f'Instead got {spc.client._counter["user_playlist_create"]} calls.'
    assert spc.client._counter['playlist_change_details'] == 1, \
        f'Expected 1 call(s) to \'playlist_change_details\' ! ' \
        f'Instead got {spc.client._counter["playlist_change_details"]} calls.'
    assert spc.client._counter['playlist_add_items'] == 1, \
        f'Expected 1 call(s) to \'playlist_add_items\' ! ' \
        f'Instead got {spc.client._counter["playlist_add_items"]} calls.'


def test_export_new_movie():
    spc = SpotifyClient()
    assert not MOCK_MOVIE_JSON['media_name'] in [x['name'] for x in spc.client._crt_playlists['items']], \
        f'Initially _crt_playlists should not contain show empty!' \
        f'Instead got: {spc.client.current_user_playlists()["items"]} .'
    uris_movie = [x['spotify'] for x in MOCK_MOVIE_JSON['songs']]
    spc.client.reset_counter()
    spc.export(playlist_name=MOCK_MOVIE_JSON_NAME_NORM,
               track_uris=uris_movie,
               description='')
    assert spc.client._counter['current_user_playlists'] == 3, \
        f'Expected 3 call(s) to \'current_user_playlists\' ! ' \
        f'Instead got {spc.client._counter["current_user_playlists"]} calls.'
    assert spc.client._counter['me'] == 1, \
        f'Expected 1 call(s) to \'me\' ! ' \
        f'Instead got {spc.client._counter["me"]} calls.'
    assert spc.client._counter['user_playlist_create'] == 1, \
        f'Expected 1 call(s) to \'user_playlist_create\' ! ' \
        f'Instead got {spc.client._counter["user_playlist_create"]} calls.'
    assert spc.client._counter['playlist_change_details'] == 1, \
        f'Expected 1 call(s) to \'playlist_change_details\' ! ' \
        f'Instead got {spc.client._counter["playlist_change_details"]} calls.'
    assert spc.client._counter['playlist_add_items'] == 1, \
        f'Expected 1 call(s) to \'playlist_add_items\' ! ' \
        f'Instead got {spc.client._counter["playlist_add_items"]} calls.'


def test_export_new_game():
    spc = SpotifyClient()
    assert not MOCK_GAME_JSON['media_name'] in [x['name'] for x in spc.client._crt_playlists['items']], \
        f'Initially _crt_playlists should not contain show empty!' \
        f'Instead got: {spc.client.current_user_playlists()["items"]} .'
    uris_game = [x['spotify'] for x in MOCK_GAME_JSON['songs']]
    spc.client.reset_counter()
    spc.export(playlist_name=MOCK_GAME_JSON_NAME_NORM,
               track_uris=uris_game,
               description='')
    assert spc.client._counter['current_user_playlists'] == 3, \
        f'Expected 3 call(s) to \'current_user_playlists\' ! ' \
        f'Instead got {spc.client._counter["current_user_playlists"]} calls.'
    assert spc.client._counter['me'] == 1, \
        f'Expected 1 call(s) to \'me\' ! ' \
        f'Instead got {spc.client._counter["me"]} calls.'
    assert spc.client._counter['user_playlist_create'] == 1, \
        f'Expected 1 call(s) to \'user_playlist_create\' ! ' \
        f'Instead got {spc.client._counter["user_playlist_create"]} calls.'
    assert spc.client._counter['playlist_change_details'] == 1, \
        f'Expected 1 call(s) to \'playlist_change_details\' ! ' \
        f'Instead got {spc.client._counter["playlist_change_details"]} calls.'
    assert spc.client._counter['playlist_add_items'] == 1, \
        f'Expected 1 call(s) to \'playlist_add_items\' ! ' \
        f'Instead got {spc.client._counter["playlist_add_items"]} calls.'


def test_export_existing_show():
    spc = SpotifyClient()
    uris_show = _get_show_uris()
    spc.export(playlist_name=MOCK_SHOW_JSON_NAME_NORM,
               track_uris=uris_show,
               description='')
    assert MOCK_SHOW_JSON_NAME_NORM in [x['name'] for x in spc.client._crt_playlists['items']], \
        f'_crt_playlists should contain show item! Instead got:  {spc.client._crt_playlists["items"]} .'
    spc.client.reset_counter()
    spc.export(playlist_name=MOCK_SHOW_JSON_NAME_NORM,
               track_uris=uris_show,
               description='')
    assert spc.client._counter['current_user_playlists'] == 6, \
        f'Expected 6 call(s) to \'current_user_playlists\' ! ' \
        f'Instead got {spc.client._counter["current_user_playlists"]} calls.'
    assert spc.client._counter['playlist_change_details'] == 1, \
        f'Expected 1 call(s) to \'playlist_change_details\' ! ' \
        f'Instead got {spc.client._counter["playlist_change_details"]} calls.'
    assert spc.client._counter['playlist_items'] == 15, \
        f'Expected 15 call(s) to \'playlist_items\' ! ' \
        f'Instead got {spc.client._counter["playlist_items"]} calls.'


def test_export_existing_movie():
    spc = SpotifyClient()
    uris_movie = [x['spotify'] for x in MOCK_MOVIE_JSON['songs']]
    spc.export(playlist_name=MOCK_MOVIE_JSON_NAME_NORM,
               track_uris=uris_movie,
               description='')
    assert MOCK_MOVIE_JSON_NAME_NORM in [x['name'] for x in spc.client._crt_playlists['items']], \
        f'_crt_playlists should contain game item! Instead got:  {spc.client._crt_playlists["items"]} .'
    spc.client.reset_counter()
    spc.export(playlist_name=MOCK_MOVIE_JSON_NAME_NORM,
               track_uris=uris_movie,
               description='')
    assert spc.client._counter['current_user_playlists'] == 6, \
        f'Expected 6 call(s) to \'current_user_playlists\' ! ' \
        f'Instead got {spc.client._counter["current_user_playlists"]} calls.'
    assert spc.client._counter['playlist_change_details'] == 1, \
        f'Expected 1 call(s) to \'playlist_change_details\' ! ' \
        f'Instead got {spc.client._counter["playlist_change_details"]} calls.'
    assert spc.client._counter['playlist_items'] == 15, \
        f'Expected 15 call(s) to \'playlist_items\' ! ' \
        f'Instead got {spc.client._counter["playlist_items"]} calls.'


def test_export_existing_game():
    spc = SpotifyClient()
    uris_game = [x['spotify'] for x in MOCK_GAME_JSON['songs']]
    spc.export(playlist_name=MOCK_GAME_JSON_NAME_NORM,
               track_uris=uris_game,
               description='')
    assert MOCK_GAME_JSON_NAME_NORM in [x['name'] for x in spc.client._crt_playlists['items']], \
        f'_crt_playlists should contain game item! Instead got:  {spc.client._crt_playlists["items"]} .'
    spc.client.reset_counter()
    spc.export(playlist_name=MOCK_GAME_JSON_NAME_NORM,
               track_uris=uris_game,
               description='')
    assert spc.client._counter['current_user_playlists'] == 6, \
        f'Expected 6 call(s) to \'current_user_playlists\' ! ' \
        f'Instead got {spc.client._counter["current_user_playlists"]} calls.'
    assert spc.client._counter['playlist_change_details'] == 1, \
        f'Expected 1 call(s) to \'playlist_change_details\' ! ' \
        f'Instead got {spc.client._counter["playlist_change_details"]} calls.'
    assert spc.client._counter['playlist_items'] == 15, \
        f'Expected 15 call(s) to \'playlist_items\' ! ' \
        f'Instead got {spc.client._counter["playlist_items"]} calls.'


def test_playlist_exists_show():
    spc = SpotifyClient()
    uris_show = _get_show_uris()
    assert not spc._playlist_exists(MOCK_SHOW_JSON_NAME_NORM), \
        f'Playlist {MOCK_SHOW_JSON_NAME_NORM} should not exist yet!'
    spc.export(playlist_name=MOCK_SHOW_JSON_NAME_NORM,
               track_uris=uris_show,
               description='')
    assert spc._playlist_exists(MOCK_SHOW_JSON_NAME_NORM), \
        f'Playlist {MOCK_SHOW_JSON_NAME_NORM} should exist now!'


def test_playlist_exists_movie():
    spc = SpotifyClient()
    uris_game = [x['spotify'] for x in MOCK_MOVIE_JSON['songs']]
    assert not spc._playlist_exists(MOCK_MOVIE_JSON_NAME_NORM), \
        f'Playlist {MOCK_MOVIE_JSON_NAME_NORM} should not exist yet!'
    spc.export(playlist_name=MOCK_MOVIE_JSON_NAME_NORM,
               track_uris=uris_game,
               description='')
    assert spc._playlist_exists(MOCK_MOVIE_JSON_NAME_NORM), \
        f'Playlist {MOCK_MOVIE_JSON_NAME_NORM} should exist now!'


def test_playlist_exists_game():
    spc = SpotifyClient()
    uris_game = [x['spotify'] for x in MOCK_GAME_JSON['songs']]
    assert not spc._playlist_exists(MOCK_GAME_JSON_NAME_NORM), \
        f'Playlist {MOCK_GAME_JSON_NAME_NORM} should not exist yet!'
    spc.export(playlist_name=MOCK_GAME_JSON_NAME_NORM,
               track_uris=uris_game,
               description='')
    assert spc._playlist_exists(MOCK_GAME_JSON_NAME_NORM), \
        f'Playlist {MOCK_GAME_JSON_NAME_NORM} should exist now!'


def test_get_playlist_id_show():
    spc = SpotifyClient()
    uris_show = _get_show_uris()
    spc.export(playlist_name=MOCK_SHOW_JSON_NAME_NORM,
               track_uris=uris_show,
               description='')
    assert spc._get_playlist_id(MOCK_SHOW_JSON_NAME_NORM) == 12, \
        f'Expected id for media {MOCK_SHOW_JSON_NAME_NORM} to be 12!'


def test_get_playlist_id_movie():
    spc = SpotifyClient()
    uris_movie = [x['spotify'] for x in MOCK_MOVIE_JSON['songs']]
    spc.export(playlist_name=MOCK_MOVIE_JSON_NAME_NORM,
               track_uris=uris_movie,
               description='')
    assert spc._get_playlist_id(MOCK_MOVIE_JSON_NAME_NORM) == 34, \
        f'Expected id for media {MOCK_MOVIE_JSON_NAME_NORM} to be 34!'


def test_get_playlist_id_game():
    spc = SpotifyClient()
    uris_game = [x['spotify'] for x in MOCK_GAME_JSON['songs']]
    spc.export(playlist_name=MOCK_GAME_JSON_NAME_NORM,
               track_uris=uris_game,
               description='')
    assert spc._get_playlist_id(MOCK_GAME_JSON_NAME_NORM) == 56, \
        f'Expected id for media {MOCK_GAME_JSON_NAME_NORM} to be 56!'


def test_get_playlist_id_non_existent():
    spc = SpotifyClient()
    assert spc._get_playlist_id(MOCK_GAME_JSON_NAME_NORM) == '', \
        f'Expected id for media {MOCK_GAME_JSON_NAME_NORM} to be empty!'


def test_item_exists_in_playlist_show():
    spc = SpotifyClient()
    uris_show = _get_show_uris()
    spc.export(playlist_name=MOCK_SHOW_JSON_NAME_NORM,
               track_uris=uris_show,
               description='')
    for uri in uris_show:
        assert spc._item_exists_in_playlist(playlist_id=spc._get_playlist_id(MOCK_SHOW_JSON_NAME_NORM),
                                            track_uri=uri)


def test_item_exists_in_playlist_movie():
    spc = SpotifyClient()
    uris_movie = [x['spotify'] for x in MOCK_MOVIE_JSON['songs']]
    spc.export(playlist_name=MOCK_MOVIE_JSON_NAME_NORM,
               track_uris=uris_movie,
               description='')
    for uri in uris_movie:
        assert spc._item_exists_in_playlist(playlist_id=spc._get_playlist_id(MOCK_MOVIE_JSON_NAME_NORM),
                                            track_uri=uri)


def test_item_exists_in_playlist_game():
    spc = SpotifyClient()
    uris_game = [x['spotify'] for x in MOCK_GAME_JSON['songs']]
    spc.export(playlist_name=MOCK_GAME_JSON_NAME_NORM,
               track_uris=uris_game,
               description='')
    for uri in uris_game:
        assert spc._item_exists_in_playlist(playlist_id=spc._get_playlist_id(MOCK_GAME_JSON_NAME_NORM),
                                            track_uri=uri)


def test_item_exists_in_playlist_non_existent():
    spc = SpotifyClient()
    uris_game = [x['spotify'] for x in MOCK_GAME_JSON['songs']]
    spc.export(playlist_name=MOCK_GAME_JSON_NAME_NORM,
               track_uris=uris_game,
               description='')
    for uri in ['as9f8h9ß', 'adza8snr', 'g7asencg']:
        assert not spc._item_exists_in_playlist(playlist_id=spc._get_playlist_id(MOCK_GAME_JSON_NAME_NORM),
                                                track_uri=uri)
