"""Scraper for Tunefind song information.

Utilizes Tunefind's undocumented API at `https://tunefind.com/api/frontend/` to
scrape information about songs and the links to respective tracks on Spotify.

Attributes:
    MEDIA_MAP (dict): Maps each MediaType to its respective scraping function.

"""

import requests

from typing import Optional

from tunefind2spotify.utils import MediaType, dict_keep


def _fetch_json(url: str) -> dict:
    """Helper function to issue a request and return JSON object from url.

    Args:
        url: The full url to which make the request to.

    Returns:
        The JSON object returned by the request.

    Raises:
        requests.RequestException: Any RequestExceptions will be logged.
    """
    try:
        resp = requests.get(url)
        print(f'{resp.status_code} | request to {url}')
        result = resp.json()
        if result:
            return result
        else:
            # TODO: Log
            raise Exception('Empty json returned from request!')  # TODO: Specify what todo in case of empty json
    except requests.RequestException as e:
        print(e)  # TODO: Log


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
            return f'spotify:track:{resp.url.split("/")[-1]}'
    except Exception as e:
        print(e)  # TODO: log
    return ''


def _scrape_show(media_name: str) -> dict:
    """Scrapes data for given media name in case of media type 'show'.

    Args:
        media_name: Name of the media as specified by Tunefind.

    Returns:
        Dictionary containing selected data about specified show.
    """
    data = dict(media_name=media_name, media_type=MediaType.SHOW, seasons=list())
    main = _fetch_json(f'https://www.tunefind.com/api/frontend/show/{media_name}?fields=seasons')
    main.update({'name': main['show']['name']})
    for s in range(len(main['seasons'])):
        season = _fetch_json(f'https://www.tunefind.com/api/frontend/show/{media_name}/season/{s + 1}?fields=episodes')
        data['seasons'].append(
                dict(name=f'Season {s+1}',
                     id=f'season/{s+1}',
                     episodes=[]
                     )
        )
        for e in range(len(season['episodes'])):
            episode_id = season['episodes'][e]['id']
            episode = _fetch_json(f'https://www.tunefind.com/api/frontend/episode/{episode_id}?fields=song-events')
            songs = []
            for se in episode['episode']['song_events']:
                song = dict_keep(se['song'], ['id', 'name', 'spotify', 'artists'])
                song.update({'artists': ', '.join([x['name'] for x in song['artists']])})
                song.update({'spotify': handle_redirect_link(f'https://www.tunefind.com{song["spotify"]}')})
                songs.append(song)
            data['seasons'][s]['episodes'].append(
                    dict(name=f'Episode {e+1}',
                         id=episode_id,
                         songs=songs
                         )
            )
    return data


def _scrape_movie(media_name: str) -> dict:
    """Scrapes data for given media name in case of MediaType.MOVIE.

    Args:
        media_name: Name of the media as specified by Tunefind.

    Returns:
        Dictionary containing selected data about specified movie.
    """
    data = dict(media_name=media_name, media_type=MediaType.MOVIE, songs=list())
    main = _fetch_json(f'https://www.tunefind.com/api/frontend/movie/{media_name}?fields=song_events')
    main.update({'name': main['movie']['name']})
    for s in main['song_events']:
        song = dict_keep(s['song'], ['id', 'name', 'spotify', 'artists'])
        song.update({'artists': ', '.join([x['name'] for x in song['artists']])})
        song.update({'spotify': handle_redirect_link(f'https://www.tunefind.com{song["spotify"]}')})
        data['songs'].append(song)
    return data


def _scrape_game(media_name: str) -> dict:
    """Scrapes data for given media name in case of MediaTYPE.GAME.


    Args:
        media_name: Name of the media as specified by Tunefind.

    Returns:
        Dictionary containing selected data about specified game.
    """
    data = dict(media_name=media_name, media_type=MediaType.GAME, songs=list())
    main = _fetch_json(f'https://www.tunefind.com/api/frontend/game/{media_name}?fields=song_events')
    main.update({'name': main['game']['name']})
    for s in main['song_events']:
        song = dict_keep(s['song'], ['id', 'name', 'spotify', 'artists'])
        song.update({'artists': ', '.join([x['name'] for x in song['artists']])})
        song.update({'spotify': handle_redirect_link(f'https://www.tunefind.com{song["spotify"]}')})
        data['songs'].append(song)
    return data


MEDIA_MAP = {MediaType.SHOW: _scrape_show,
             MediaType.MOVIE: _scrape_movie,
             MediaType.GAME: _scrape_game}


def _name_and_type_check(media_name: str, media_type: MediaType) -> (str, MediaType):
    """Checks whether the resource exists on tunefind.com.

    This function will check for existence of the resource including actions to
    normalize the media name, probe different media types in case `None` was
    given.

    Args:
        media_name: Name of the media as specified by Tunefind.
        media_type: Type of media as in the categories found on Tunefind. Must
            be one of `MediaType` enum values or `None` in which case the
            correct media type will be inferred from probing Tunefind.

    Returns:
        Media name and type, corrected if necessary.

    Raises:
        Exception: If resource is not found on tunefind.com.
        requests.RequestException: Any RequestExceptions will be logged.
    """
    print(media_type, type(media_type))
    correct_media_type = media_type if media_type is not None and media_type in MediaType else ''
    correct_media = media_name.lower().replace(' ', '-').replace('_', '-')

    def resource_exists(media_name: str, media_type: MediaType):
        exists = False
        try:
            print(f'probing: https://www.tunefind.com/api/frontend/{MediaType.translate(media_type)}/{media_name}')
            exists = requests.get(
                    f'https://www.tunefind.com/api/frontend/{MediaType.translate(media_type)}/{media_name}'
            ).status_code == 200
        except requests.RequestException as e:
            print(e)  # TODO: Log
        finally:
            return exists

    # Probe different media types if resource does not exist for given media
    # type or was not given at all (`None`)
    if not resource_exists(correct_media, correct_media_type):
        correct_media_type = None
        for media in MediaType:
            try:
                if resource_exists(correct_media, media):
                    correct_media_type = media
                    break
            except requests.RequestException as e:
                print(e)  # TODO: Log
        if correct_media_type is None:
            raise Exception()  # TODO: Specify error raised if resource is not found

    return correct_media, correct_media_type


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
    return MEDIA_MAP[media_type](media_name)
