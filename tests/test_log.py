"""Test module for `tunefind2spotify.log`."""

from tunefind2spotify.log import _LOG_LEVEL,\
                                 fetch_logger,\
                                 flatten_multiline_string as fms


def test_fetch_logger():
    logger = fetch_logger(__name__)
    assert logger.level == _LOG_LEVEL, 'TODO'
    assert logger.name == __name__, 'TODO'
    assert len(logger.handlers) == 2, 'TODO'


def test_flatten_multiline_string():
    in_ = """ test
             test2
                test3
    """
    out_ = 'test test2 test3'
    assert fms(in_) == out_, f'Result should equal \'{out_}\'.'
