"""Mock of module `tunefind2spotify.db`.

To be used as surrogate for above mentioned module during testing.

Wraps initialization of `tunefind2spotify.db.DBConnector` to alter the path
where the data base during testing is located. Prevents that test data is
written into production data base.By default the database file is recreated for
each call to the `__init__`. Set `tests.mock_db.REUSE = True` in test cases that
require test data base content to persist over multiple calls to the object's
`__init__`.

The module logger is also monkey patched with a logger that writes into a
`StringIO` object. For testing purposes, logged content can be read from
`*module*.string_capture`.

Via module-level `__getattr__` the (remaining) namespace of the mocked module is
made available to the importer of the module.
"""

import os

from tunefind2spotify import db

from tests.mock_logger import mock_logger


REUSE = False


def _get_mock_db_file(reuse: bool):
    parent_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_data')
    test_db_path = os.path.join(parent_dir, 'test.db')
    if os.path.isdir(parent_dir):
        if os.path.isfile(test_db_path) and not reuse:
            os.remove(test_db_path)
    else:
        os.makedirs(parent_dir)
    return test_db_path


def wrap_init(func):
    def mock_init_db(self, *args, **kwargs):
        return func(self, db_filepath=_get_mock_db_file(REUSE))
    return mock_init_db


# monkey patch module
logger, string_capture = mock_logger(__name__)
db.logger = logger
db.string_capture = string_capture
db.DBConnector.__init__ = wrap_init(db.DBConnector.__init__)


def __getattr__(name):
    return getattr(db, name)


def __setattr__(name, value):
    setattr(db, name, value)
