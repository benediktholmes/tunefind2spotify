"""Mock of module `tunefind2spotify.core.tunefind_scraper`.

To be used as surrogate for above mentioned module during testing.

Module functions making web requests are monkey patched with functions mocking
their original functionality and returning correct data using sample test data
@ `tests.test_data.mock_json_data`. Prevents that actual website scraping is
executed during testing. Implies that successful tests are only valid while the
sample data matches the data scheme from the API.

The module logger is also monkey patched with a logger that writes into a
`StringIO` object. For testing purposes, logged content can be read from
`*module*.string_capture`.

Via module-level `__getattr__` the (remaining) namespace of the mocked module is
made available to the importer of the module.
"""

import copy
import random

from tunefind2spotify.core import tunefind_scraper
from tunefind2spotify.utils import MediaType

from tests.mock_logger import mock_logger
from tests.test_data.mock_json_data import \
    MOCK_SHOW_JSON, \
    MOCK_MOVIE_JSON, \
    MOCK_GAME_JSON


def mock_fetch_json(url):  # noqa: C901
    url_split = url.split('?')[0].split('/')
    if url.endswith('?fields=seasons'):
        return {'show': {'name': url_split[-1]}, 'seasons': [len(MOCK_SHOW_JSON['seasons'])]}
    elif url.endswith('?fields=episodes'):
        season = int(url_split[-1]) - 1
        return {'episodes': [{'id': x['id']} for x in MOCK_SHOW_JSON['seasons'][season]['episodes']]}
    elif url.endswith('?fields=song-events'):
        if url_split[-2] == 'episode':
            episodes = []
            for s in MOCK_SHOW_JSON['seasons']:
                episodes.extend(s['episodes'])
            episode = [e['songs'] for e in episodes if e['id'] == int(url_split[-1])][0]
            x = {'episode': {'song_events': [{'song': copy.deepcopy(x)} for x in episode]}}
            for i in range(len(x['episode']['song_events'])):
                x['episode']['song_events'][i]['song']['artists'] = \
                    [{'name': x['episode']['song_events'][i]['song']['artists']}]
            return x
        elif url_split[-2] == 'movie':
            x = {'movie': {'name': url_split[-1]}, 'song_events': [{'song': copy.deepcopy(x)}
                                                                   for x in MOCK_MOVIE_JSON['songs']]}
            for i in range(len(x['song_events'])):
                x['song_events'][i]['song']['artists'] = \
                    [{'name': x['song_events'][i]['song']['artists']}]
            return x
        elif url_split[-2] == 'game':
            x = {'game': {'name': url_split[-1]}, 'song_events': [{'song': copy.deepcopy(x)}
                                                                  for x in MOCK_GAME_JSON['songs']]}
            for i in range(len(x['song_events'])):
                x['song_events'][i]['song']['artists'] = \
                    [{'name': x['song_events'][i]['song']['artists']}]
            return x
    return {}


def mock_handle_redirect(*x):
    return ''


def _get(url):

    class MockRequestReturn:
        def __init__(self, status_code):
            self.status_code = status_code

    url_split = url.split('/')
    if 'forward' in url_split:
        return MockRequestReturn(random.choice([302, 404]))
    elif MediaType.read_in(url_split[-2]) is not None:  # noqa: F821
        if (MediaType.read_in(url_split[-2]) == MediaType.SHOW and url_split[-1] == MOCK_SHOW_JSON['media_name']) or \
           (MediaType.read_in(url_split[-2]) == MediaType.MOVIE and url_split[-1] == MOCK_MOVIE_JSON['media_name']) or \
           (MediaType.read_in(url_split[-2]) == MediaType.GAME and url_split[-1] == MOCK_GAME_JSON['media_name']):
            return MockRequestReturn(200)
        else:
            return MockRequestReturn(404)
    else:
        None


# monkey patch module
logger, string_capture = mock_logger(__name__)
tunefind_scraper.logger = logger
tunefind_scraper.string_capture = string_capture
tunefind_scraper._fetch_json = mock_fetch_json
tunefind_scraper.handle_redirect_link = mock_handle_redirect
tunefind_scraper.requests.get = _get


def __getattr__(name):
    return getattr(tunefind_scraper, name)


def __setattr__(name, value):
    setattr(tunefind_scraper, name, value)
