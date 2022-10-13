"""Test module for `tunefind2spotify.exceptions`."""

import os
import pytest

from tunefind2spotify import exceptions

from tests.mock_logger import mock_logger


def test_log_and_raise_exception_class():
    logger, string_capture = mock_logger(__name__)
    for e in [exceptions.MediaNotFound, exceptions.EmptyJSONResponse, exceptions.MissingCredentialsException]:
        with pytest.raises(e):
            exceptions.log_and_raise(logger, e, e.__name__)
        log_string = string_capture.getvalue().split(os.linesep)[-2]  # always get the newest logged line
        assert log_string == f'ERROR: {e.__name__}'
    string_capture.close()


def test_log_and_raise_exception_instance():
    logger, string_capture = mock_logger(__name__)
    for e in [exceptions.MediaNotFound, exceptions.EmptyJSONResponse, exceptions.MissingCredentialsException]:
        with pytest.raises(e):
            exceptions.log_and_raise(logger, e(), e.__name__)
        log_string = string_capture.getvalue().split(os.linesep)[-2]  # always get the newest logged line
        assert log_string == f'ERROR: {e.__name__}'
    string_capture.close()
