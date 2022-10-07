import pytest

from tunefind2spotify.utils import MediaType

from tests import mock_tunefind_scraper as tunefind_scraper
from tests.test_data.mock_json_data import \
    MOCK_SHOW_JSON, \
    MOCK_MOVIE_JSON, \
    MOCK_GAME_JSON, \
    MOCK_SHOW_JSON_NAME_NORM, \
    MOCK_MOVIE_JSON_NAME_NORM, \
    MOCK_GAME_JSON_NAME_NORM


def test_mock_get():
    assert tunefind_scraper._resource_exists(MOCK_SHOW_JSON_NAME_NORM, MediaType.SHOW), \
        'Mock should return True!'
    assert tunefind_scraper._resource_exists(MOCK_MOVIE_JSON_NAME_NORM, MediaType.MOVIE), \
        'Mock should return True!'
    assert tunefind_scraper._resource_exists(MOCK_GAME_JSON_NAME_NORM, MediaType.GAME), \
        'Mock should return True!'
    assert not tunefind_scraper._resource_exists('8hsg094g', media_type=MediaType.SHOW), \
        'Mock should return False!'


def test_scrape_wo_media_type():
    tunefind_scraper.scrape(MOCK_SHOW_JSON['media_name'])
    tunefind_scraper.scrape(MOCK_MOVIE_JSON['media_name'])
    tunefind_scraper.scrape(MOCK_GAME_JSON['media_name'])


def test_scrape_wo_media_type_repeating():
    tunefind_scraper.scrape(MOCK_SHOW_JSON['media_name'])
    tunefind_scraper.scrape(MOCK_SHOW_JSON['media_name'])
    tunefind_scraper.scrape(MOCK_MOVIE_JSON['media_name'])
    tunefind_scraper.scrape(MOCK_MOVIE_JSON['media_name'])
    tunefind_scraper.scrape(MOCK_GAME_JSON['media_name'])
    tunefind_scraper.scrape(MOCK_GAME_JSON['media_name'])


def test_scrape_w_media_type():
    tunefind_scraper.scrape(MOCK_SHOW_JSON['media_name'], MediaType.SHOW)
    tunefind_scraper.scrape(MOCK_MOVIE_JSON['media_name'], MediaType.MOVIE)
    tunefind_scraper.scrape(MOCK_GAME_JSON['media_name'], MediaType.GAME)


def test_scrape_w_media_type_to_be_corrected():
    tunefind_scraper.scrape(MOCK_SHOW_JSON['media_name'], MediaType.MOVIE)
    tunefind_scraper.scrape(MOCK_MOVIE_JSON['media_name'], MediaType.GAME)
    tunefind_scraper.scrape(MOCK_GAME_JSON['media_name'], MediaType.SHOW)


def test_scrape_w_media_name_already_correct():
    tunefind_scraper.scrape(MOCK_SHOW_JSON_NAME_NORM, MediaType.SHOW)
    tunefind_scraper.scrape(MOCK_MOVIE_JSON_NAME_NORM, MediaType.MOVIE)
    tunefind_scraper.scrape(MOCK_GAME_JSON_NAME_NORM, MediaType.GAME)


def test_infer_non_existent_media_type():
    with pytest.raises(tunefind_scraper.MediaNotFound):
        tunefind_scraper._infer_media_type('srfgdv98')
