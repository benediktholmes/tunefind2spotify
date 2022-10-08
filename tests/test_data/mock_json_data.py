"""Exemplary data used for testing purposes."""

from tunefind2spotify.utils import MediaType

MOCK_SHOW_JSON = {'media_name': 'the-mocks',
                  'media_type': MediaType.SHOW,
                  'readable_name': 'The Mocks',
                  'seasons': [
                      {'name': 'Season 1',
                       'id': 'season/1',
                       'episodes': [
                           {'name': 'Episode 1',
                            'id': 110,
                            'songs': [
                                {'id': 111,
                                 'name': 'This is a test.',
                                 'spotify': 'spotify:track:DEADBEEF',
                                 'artists': 'The author'},
                                {'id': 112,
                                 'name': 'It\' so fluffy!',
                                 'spotify': 'spotify:track:unicorn',
                                 'artists': 'Agnes'}
                            ]},
                           {'name': 'Episode 2',
                            'id': 120,
                            'songs': [
                                {'id': 121,
                                 'name': 'This is a another test.',
                                 'spotify': 'spotify:track:C0FEBABE',
                                 'artists': 'The author'},
                                {'id': 122,
                                 'name': 'It\' so fluufffffy!!!',
                                 'spotify': 'spotify:track:UNICORN',
                                 'artists': 'Agnes'}
                            ]}
                       ]},
                      {'name': 'Season 2',
                       'id': 'season/2',
                       'episodes': [
                           {'name': 'Episode 1',
                            'id': 210,
                            'songs': [
                                {'id': 211,
                                 'name': 'No name.',
                                 'spotify': 'spotify:track:empty',
                                 'artists': 'No one.'}
                            ]}
                       ]}
                  ]}


MOCK_MOVIE_JSON = {'media_name': 'mockies-adventures',
                   'media_type': MediaType.MOVIE,
                   'readable_name': 'Mockies Adventures',
                   'songs': [
                       {'id': 5,
                        'name': 'This is a test.',
                        'spotify': 'spotify:track:DEADBEEF',
                        'artists': 'The author'},
                       {'id': 6,
                        'name': 'It\' so fluffy!',
                        'spotify': 'spotify:track:unicorn',
                        'artists': 'Agnes'},
                       {'id': 7,
                        'name': 'This is a another test.',
                        'spotify': 'spotify:track:C0FEBABE',
                        'artists': 'The author'},
                       {'id': 8,
                        'name': 'It\' so fluufffffy!!!',
                        'spotify': 'spotify:track:UNICORN',
                        'artists': 'Agnes'},
                       {'id': 9,
                        'name': 'No name.',
                        'spotify': 'spotify:track:empty',
                        'artists': 'No one.'}
                   ]}


MOCK_GAME_JSON = {'media_name': 'mockricilious',
                  'media_type': MediaType.GAME,
                  'readable_name': 'Mockricilious',
                  'songs': [
                      {'id': 0,
                       'name': 'This is a test.',
                       'spotify': 'spotify:track:DEADBEEF',
                       'artists': 'The author'},
                      {'id': 1,
                       'name': 'It\' so fluffy!',
                       'spotify': 'spotify:track:unicorn',
                       'artists': 'Agnes'},
                      {'id': 2,
                       'name': 'This is a another test.',
                       'spotify': 'spotify:track:C0FEBABE',
                       'artists': 'The author'},
                      {'id': 3,
                       'name': 'It\' so fluufffffy!!!',
                       'spotify': 'spotify:track:UNICORN',
                       'artists': 'Agnes'},
                      {'id': 4,
                       'name': 'No name.',
                       'spotify': 'spotify:track:empty',
                       'artists': 'No one.'}
                  ]}


def _get_show_uris():
    x = []
    for item_ in MOCK_SHOW_JSON['seasons']:
        x.extend(item_['episodes'])
    y = []
    for item_ in x:
        y.extend(item_['songs'])
    z = []
    for item_ in y:
        z.append(item_['spotify'])
    return z
