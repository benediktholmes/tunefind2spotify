"""Scraper for Tunefind song information.

Utilizes Tunefind's undocumented API at `https://tunefind.com/api/frontend/` to
scrape information about songs and the links to respective tracks on Spotify.

Attributes:
    MEDIA_MAP (dict): Maps each MediaType to its respective scraping function.

"""

import requests

from typing import Optional

from tqdm import tqdm

from tunefind2spotify.exceptions import log_and_raise, EmptyJSONResponse, MediaNotFound
from tunefind2spotify.log import fetch_logger
from tunefind2spotify.utils import MediaType, dict_keep


logger = fetch_logger(__name__)

API = 'https://www.tunefind.com/api/frontend'


def _fetch_json(url: str) -> dict:
    """Helper function to issue a request and return JSON object from url.

    Args:
        url: The full url to which make the request to.

    Returns:
        The JSON object returned by the request.

    Raises:
        EmptyJSONResponse: In case returned JSON is empty.
        requests.RequestException: Any Exception with the request.
    """
    try:
        resp = requests.get(url)
        logger.debug(f'Response {resp.status_code} for request to {url}')
        result = resp.json()
        if result:
            return result
        else:
            # TODO: Now fails on first attempt. In future maybe implement retry?
            log_and_raise(logger, EmptyJSONResponse, 'Empty json returned from request!')
    except requests.RequestException as e:
        log_and_raise(logger, e, '')


def handle_redirect_link(url: str) -> str:
    """Handles Tunefind's Spotify track links and returns correct track URI.

    Note:
        Tunefind's links to tracks on Spotify are short-dated single redirects
        that must be resolved at scraping time. Further, Spotify track URLs are
        immediately converted to track URIs.

    Args:
        url: The url to be handled.

    Returns:
        The correct Spotify URI or empty string in any other case.
    """
    try:
        resp = requests.get(url, allow_redirects=False)
        if resp.status_code == 302:
            resp = requests.get(url, allow_redirects=True)
            x = f'spotify:track:{resp.url.split("/")[-1]}'
            logger.debug(f'Replaced forward link \'{url}\' -> \'{x}\'.')
            return x
        else:
            logger.debug(f'No redirect for url: \'{url}\'.')
    except Exception as e:
        log_and_raise(logger, e, '')
    return ''


def _scrape_show(media_name: str) -> dict:
    """Scrapes data for given media name in case of media type 'show'.

    Args:
        media_name: Name of the media as specified by Tunefind.

    Returns:
        Dictionary containing selected data about specified show.
            - `media_name`: Name of media.
            - `media_type`: Type of media.
            - `seasons`: List of dictionaries with keys:
                - `id`: Tunefind ID of season.
                - `name`: Name of season.
                - `episodes`: List of dictionaries with keys:
                    - `id`: Tunefind ID of episode.
                    - `name`: Name of episode.
                    - `songs`: List of dictionaries with keys:
                        - `id`: Tunefind ID of song.
                        - `name`: Name of song.
                        - `spotify`: Spotify track URI.
                        - `artists`: String of comma-separated artists.
    """
    data = dict(media_name=media_name, media_type=MediaType.SHOW, seasons=list())
    main = _fetch_json(f'{API}/show/{media_name}?fields=seasons')
    main.update({'name': main['show']['name']})  # TODO: Relevance?
    for s in range(len(main['seasons'])):
        season = _fetch_json(f'{API}/show/{media_name}/season/{s + 1}?fields=episodes')
        data['seasons'].append(
                dict(name=f'Season {s+1}',
                     id=f'season/{s+1}',
                     episodes=[]
                     )
        )
        for e in range(len(season['episodes'])):
            episode_id = season['episodes'][e]['id']
            episode = _fetch_json(f'{API}/episode/{episode_id}?fields=song-events')
            songs = []
            for se in tqdm(episode['episode']['song_events'],
                           desc=f'Scraping season {s+1} episode {e+1}',
                           disable=False):
                song = dict_keep(se['song'], ['id', 'name', 'spotify', 'artists'])
                song.update({'artists': ', '.join([x['name'] for x in song['artists']])})
                song.update({'spotify': '' if song['spotify'] is None
                             else handle_redirect_link(f'https://www.tunefind.com{song["spotify"]}')})
                songs.append(song)
            data['seasons'][s]['episodes'].append(
                    dict(name=f'Episode {e+1}',
                         id=episode_id,
                         songs=songs
                         )
            )
    y = []
    for x in [x["episodes"] for x in data["seasons"]]:
        y.extend(x)
    logger.info(f'Found {len(data["seasons"])} seasons, '
                f'{sum([len(x["episodes"]) for x in data["seasons"]])} episodes, '
                f'{sum([sum([len(x["songs"]) for x in y])])} songs in total.')
    return data


def _scrape_movie(media_name: str) -> dict:
    """Scrapes data for given media name in case of MediaType.MOVIE.

    Args:
        media_name: Name of the media as specified by Tunefind.

    Returns:
        Dictionary containing selected data about specified movie.
            - `media_name`: Name of media.
            - `media_type`: Type of media.
            - `songs`: List of dictionaries with keys:
                - `id`: Tunefind ID of song.
                - `name`: Name of song.
                - `spotify`: Spotify track URI.
                - `artists`: String of comma-separated artists.
    """
    data = dict(media_name=media_name, media_type=MediaType.MOVIE, songs=list())
    main = _fetch_json(f'{API}/movie/{media_name}?fields=song-events')
    main.update({'name': main['movie']['name']})  # TODO: Relevance?
    for s in tqdm(main['song_events'],
                  desc='Scraping songs',
                  disable=False):
        song = dict_keep(s['song'], ['id', 'name', 'spotify', 'artists'])
        song.update({'artists': ', '.join([x['name'] for x in song['artists']])})
        song.update({'spotify': '' if song['spotify'] is None
                     else handle_redirect_link(f'https://www.tunefind.com{song["spotify"]}')})
        data['songs'].append(song)
    logger.info(f'Found {len(data["songs"])} songs in total.')
    return data


def _scrape_game(media_name: str) -> dict:
    """Scrapes data for given media name in case of MediaTYPE.GAME.

    Args:
        media_name: Name of the media as specified by Tunefind.

    Returns:
        Dictionary containing selected data about specified game:
            - `media_name`: Name of media.
            - `media_type`: Type of media.
            - `songs`: List of dictionaries with keys:
                - `id`: Tunefind ID of song.
                - `name`: Name of song.
                - `spotify`: Spotify track URI.
                - `artists`: String of comma-separated artists.
    """
    data = dict(media_name=media_name, media_type=MediaType.GAME, songs=list())
    main = _fetch_json(f'{API}/game/{media_name}?fields=song-events')
    main.update({'name': main['game']['name']})  # TODO: Relevance?
    for s in tqdm(main['song_events'],
                  desc='Scraping songs',
                  disable=False):
        song = dict_keep(s['song'], ['id', 'name', 'spotify', 'artists'])
        song.update({'artists': ', '.join([x['name'] for x in song['artists']])})
        song.update({'spotify': '' if song['spotify'] is None
                     else handle_redirect_link(f'https://www.tunefind.com{song["spotify"]}')})
        data['songs'].append(song)
    logger.info(f'Found {len(data["songs"])} songs in total.')
    return data


MEDIA_MAP = {MediaType.SHOW: _scrape_show,
             MediaType.MOVIE: _scrape_movie,
             MediaType.GAME: _scrape_game}


def _resource_exists(media_name: str, media_type: MediaType) -> bool:
    """Checks whether combination of media name and type exists on Tunefind.

     Note:
        Check is based on HTTP 200 response when querying the Tunefind API for
        given media name and a media type. Will use the first match, as media
        names on Tunefind are unique.

    Args:
        media_name: Name of media to be checked.
        media_type: Type of media to be checked.

    Returns:
        True, if the media exists, else False.

    Raises:
        requests.RequestException: Any Exception with the request.
    """
    exists = False
    try:
        logger.debug(f'Probing media type \'{str(media_type)}\': {API}/{MediaType.translate(media_type)}/{media_name}')
        exists = requests.get(f'{API}/{MediaType.translate(media_type)}/{media_name}').status_code == 200
    except requests.RequestException as e:
        log_and_raise(logger, e, '')
    return exists


def _infer_media_type(media_name: str) -> (str, MediaType):
    """Infers type of media given its name.

    Args:
        media_name: The name of media for which type shall be inferred.

    Returns:
        Tuple of media name and inferred type.

    Raises:
        requests.RequestException: Any Exception with the request.
        MediaNotFound: If resource is not found on Tunefind.
    """
    correct_media_type = None
    for media in MediaType:
        try:
            if _resource_exists(media_name, media):
                correct_media_type = media
                break
        except requests.RequestException as e:
            log_and_raise(logger, e, '')
    if correct_media_type is None:
        log_and_raise(logger, MediaNotFound, f'No media could be found for name \'{media_name}\'. Typo?')

    return media_name, correct_media_type


def _name_and_type_check(media_name: str, media_type: MediaType) -> (str, MediaType):
    """Checks whether the resource exists on Tunefind.


    This function will check for existence of the resource including actions to
    normalize the media name and/or probe different media types in case the one
    specified does not exist or `None` was passed.

    Args:
        media_name: Name of the media as specified by Tunefind.
        media_type: Type of media as in the categories found on Tunefind. Must
            be one of `MediaType` enum values or `None` in which case the
            correct media type will be inferred from probing Tunefind API.

    Returns:
        Media name and type, corrected if necessary.
    """
    correct_media_name = media_name.lower().replace(' ', '-').replace('_', '-')
    if media_name != correct_media_name:
        logger.info(f'Automatically corrected `media_name` from \'{media_name}\' to \'{correct_media_name}\'.')
    correct_media_type = media_type if isinstance(media_type, MediaType) else ''

    recheck_necessary = True
    if correct_media_type == '':
        logger.info('No media type given, will be inferred.')
    elif not _resource_exists(correct_media_name, correct_media_type):
        logger.info(f'No media found for type \'{str(correct_media_type)}\'.')
    else:
        recheck_necessary = False

    # Probe different media types if resource does not exist for given media
    # type or was not given at all (`None`)
    if recheck_necessary:
        correct_media_name, correct_media_type = _infer_media_type(correct_media_name)
    logger.info(f'Verified existence of media \'{media_name}\' with type \'{str(correct_media_type)}\'.')
    return correct_media_name, correct_media_type


def scrape(media_name: str, media_type: Optional[MediaType] = None) -> dict:
    """Scrapes the song information from Tunefind's frontend API.

    Prior to collecting the data, normalization of the given media name and also
    an inference of the media type are performed. Will then invoke the scraping
    method implemented for the specific media type.

    Args:
        media_name: Name of the media as specified by Tunefind.
        media_type: Type of media as in the categories found on Tunefind. Must
            be one of `MediaType` enum values. Optional, defaults to `None` in
            which case the correct media type will be inferred from probing
            Tunefind.

    Returns:
        A (nested) dictionary object corresponding to the JSON holding the
        relevant scraped information.
    """
    media_name, media_type = _name_and_type_check(media_name, media_type)
    logger.info(f'Scraping \'{media_name}\' from Tunefind ...')
    return MEDIA_MAP[media_type](media_name)
