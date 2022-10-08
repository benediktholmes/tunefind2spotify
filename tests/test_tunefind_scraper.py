import pytest

from tunefind2spotify.utils import MediaType

from tests import mock_tunefind_scraper as tunefind_scraper
from tests.test_data.mock_json_data import \
    MOCK_SHOW_JSON, \
    MOCK_MOVIE_JSON, \
    MOCK_GAME_JSON


def test_ressource_exists():
    assert tunefind_scraper._resource_exists(MOCK_SHOW_JSON['media_name'], MediaType.SHOW)
    assert not tunefind_scraper._resource_exists(MOCK_SHOW_JSON['media_name'], MediaType.MOVIE)
    assert not tunefind_scraper._resource_exists(MOCK_SHOW_JSON['media_name'], MediaType.GAME)
    assert not tunefind_scraper._resource_exists(MOCK_MOVIE_JSON['media_name'], MediaType.SHOW)
    assert tunefind_scraper._resource_exists(MOCK_MOVIE_JSON['media_name'], MediaType.MOVIE)
    assert not tunefind_scraper._resource_exists(MOCK_MOVIE_JSON['media_name'], MediaType.GAME)
    assert not tunefind_scraper._resource_exists(MOCK_GAME_JSON['media_name'], MediaType.SHOW)
    assert not tunefind_scraper._resource_exists(MOCK_GAME_JSON['media_name'], MediaType.MOVIE)
    assert tunefind_scraper._resource_exists(MOCK_GAME_JSON['media_name'], MediaType.GAME)


def test_infer_media_type():
    for m in [MOCK_SHOW_JSON, MOCK_MOVIE_JSON, MOCK_GAME_JSON]:
        x, y = tunefind_scraper._infer_media_type(m['media_name'])
        assert x == m['media_name']
        assert y == m['media_type']


def test_name_normalization():
    test_data = {
        ' test 1 2 3': 'test-1-2-3',
        'snake_case': 'snake-case',
        ' M R O ': 'm-r-o',
        'CamelCase': 'camelcase'
    }
    for k, v in test_data.items():
        assert (x := tunefind_scraper.name_normalization(k)) == v,\
            f'After normalization \'{x}\' (formerly \'{k}\') should match \'{v}\' .'


def test_name_and_type_check():
    for m in [MOCK_SHOW_JSON, MOCK_MOVIE_JSON, MOCK_GAME_JSON]:
        for mt in MediaType:
            for name in ['media_name', 'readable_name']:
                x, y = tunefind_scraper.name_and_type_check(m[name], mt)
                assert x == m['media_name']
                assert y == m['media_type']


def test_mock_get():
    assert tunefind_scraper._resource_exists(MOCK_SHOW_JSON['media_name'], MediaType.SHOW), \
        'Mock should return True!'
    assert tunefind_scraper._resource_exists(MOCK_MOVIE_JSON['media_name'], MediaType.MOVIE), \
        'Mock should return True!'
    assert tunefind_scraper._resource_exists(MOCK_GAME_JSON['media_name'], MediaType.GAME), \
        'Mock should return True!'
    assert not tunefind_scraper._resource_exists('8hsg094g', media_type=MediaType.SHOW), \
        'Mock should return False!'


def test_scrape_wo_media_type():
    tunefind_scraper.scrape(MOCK_SHOW_JSON['media_name'])
    tunefind_scraper.scrape(MOCK_MOVIE_JSON['media_name'])
    tunefind_scraper.scrape(MOCK_GAME_JSON['media_name'])


def test_scrape_wo_media_type_readable():
    tunefind_scraper.scrape(MOCK_SHOW_JSON['readable_name'])
    tunefind_scraper.scrape(MOCK_MOVIE_JSON['readable_name'])
    tunefind_scraper.scrape(MOCK_GAME_JSON['readable_name'])


def test_scrape_wo_media_type_repeating():
    tunefind_scraper.scrape(MOCK_SHOW_JSON['media_name'])
    tunefind_scraper.scrape(MOCK_SHOW_JSON['media_name'])
    tunefind_scraper.scrape(MOCK_MOVIE_JSON['media_name'])
    tunefind_scraper.scrape(MOCK_MOVIE_JSON['media_name'])
    tunefind_scraper.scrape(MOCK_GAME_JSON['media_name'])
    tunefind_scraper.scrape(MOCK_GAME_JSON['media_name'])


def test_scrape_wo_media_type_readable_repeating():
    tunefind_scraper.scrape(MOCK_SHOW_JSON['readable_name'])
    tunefind_scraper.scrape(MOCK_SHOW_JSON['readable_name'])
    tunefind_scraper.scrape(MOCK_MOVIE_JSON['readable_name'])
    tunefind_scraper.scrape(MOCK_MOVIE_JSON['readable_name'])
    tunefind_scraper.scrape(MOCK_GAME_JSON['readable_name'])
    tunefind_scraper.scrape(MOCK_GAME_JSON['readable_name'])


def test_scrape_w_media_type():
    tunefind_scraper.scrape(MOCK_SHOW_JSON['media_name'], MediaType.SHOW)
    tunefind_scraper.scrape(MOCK_MOVIE_JSON['media_name'], MediaType.MOVIE)
    tunefind_scraper.scrape(MOCK_GAME_JSON['media_name'], MediaType.GAME)


def test_scrape_w_media_type_readable():
    tunefind_scraper.scrape(MOCK_SHOW_JSON['readable_name'], MediaType.SHOW)
    tunefind_scraper.scrape(MOCK_MOVIE_JSON['readable_name'], MediaType.MOVIE)
    tunefind_scraper.scrape(MOCK_GAME_JSON['readable_name'], MediaType.GAME)


def test_scrape_w_media_type_to_be_corrected():
    tunefind_scraper.scrape(MOCK_SHOW_JSON['media_name'], MediaType.MOVIE)
    tunefind_scraper.scrape(MOCK_MOVIE_JSON['media_name'], MediaType.GAME)
    tunefind_scraper.scrape(MOCK_GAME_JSON['media_name'], MediaType.SHOW)


def test_scrape_w_media_type_to_be_corrected_readable():
    tunefind_scraper.scrape(MOCK_SHOW_JSON['readable_name'], MediaType.MOVIE)
    tunefind_scraper.scrape(MOCK_MOVIE_JSON['readable_name'], MediaType.GAME)
    tunefind_scraper.scrape(MOCK_GAME_JSON['readable_name'], MediaType.SHOW)


def test_scrape_w_media_name_already_correct():
    tunefind_scraper.scrape(MOCK_SHOW_JSON['media_name'], MediaType.SHOW)
    tunefind_scraper.scrape(MOCK_MOVIE_JSON['media_name'], MediaType.MOVIE)
    tunefind_scraper.scrape(MOCK_GAME_JSON['media_name'], MediaType.GAME)


def test_scrape_w_media_name_already_correct_readable():
    tunefind_scraper.scrape(MOCK_SHOW_JSON['readable_name'], MediaType.SHOW)
    tunefind_scraper.scrape(MOCK_MOVIE_JSON['readable_name'], MediaType.MOVIE)
    tunefind_scraper.scrape(MOCK_GAME_JSON['readable_name'], MediaType.GAME)


def test_infer_non_existent_media_type():
    with pytest.raises(tunefind_scraper.MediaNotFound):
        tunefind_scraper._infer_media_type('srfgdv98')
