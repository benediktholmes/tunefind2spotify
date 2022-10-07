"""Mock of module `tunefind2spotify.main`.

To be used as surrogate for above mentioned module during testing.

Monkey patches the relevant project's modules used by `tunefind2spotify.main`
with their mocked counterparts.

The module logger is also monkey patched with a logger that writes into a
`StringIO` object. For testing purposes, logged content can be read from
`*module*.string_capture`.

Via module-level `__getattr__` the (remaining) namespace of the mocked module is
made available to the importer of the module.
"""

from tunefind2spotify import main

from tests import mock_tunefind_scraper
from tests import mock_spotify_client
from tests import mock_db
from tests.mock_logger import mock_logger


# monkey patch module
logger, string_capture = mock_logger(__name__)
main.logger = logger
main.string_capture = string_capture
main.tunefind_scraper = mock_tunefind_scraper
main.db = mock_db
main.spotify_client = mock_spotify_client


def __getattr__(name):
    return getattr(main, name)


def __setattr__(name, value):
    setattr(main, name, value)
