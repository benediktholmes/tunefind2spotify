"""Mock logger to use when testing.

To use, import this module in the mock module, create mock logger and monkey
patch original logger module, as so:

```
# mock_for_module.py
from tests.mock_logger import mock_logger

mock_logger, string_capture = mock_logger(__name__)
mocked_module.logger = logger
mocked_module.string_capture = string_capture
```

"""

import io
import logging


def mock_logger(name: str) -> (logging.Logger, io.StringIO):
    """Logger factory that imitates logger creation in `tunefind2spotify.log`.

    Will create a named logger that writes only into a StringIO object.

    Returns:
        The named logger object
        Reference to the StringIO object into which the logger writes. Has a
            `reset` method to intermediately clear log during testing.

    """
    def reset():
        string_capture.truncate(0)
        string_capture.seek(0)

    mock_logger_ = logging.Logger(name + '__test__')
    mock_logger_.setLevel(logging.DEBUG)
    string_capture = io.StringIO()
    string_capture.__setattr__('reset', reset)
    ch = logging.StreamHandler(string_capture)
    sf = logging.Formatter(fmt='%(levelname)s: %(message)s')
    ch.setFormatter(sf)
    mock_logger_.addHandler(ch)
    return mock_logger_, string_capture
