"""Factory and utils for module specific logging."""

import logging

_LOG_LEVEL = logging.INFO  # DEBUG


def fetch_logger(name: str) -> logging.Logger:
    """Returns a named logger instance."""
    logger = logging.getLogger(name)
    logger.setLevel(_LOG_LEVEL)

    fh = logging.FileHandler(filename='t2s.log', mode='a', )
    ff = logging.Formatter(fmt='%(asctime)s | %(levelname)s:%(name)s:%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    fh.setFormatter(ff)
    logger.addHandler(fh)

    sh = logging.StreamHandler()
    sf = logging.Formatter(fmt='%(levelname)s: %(message)s')
    sh.setFormatter(sf)
    logger.addHandler(sh)
    return logger


def flatten_multiline_string(x: str) -> str:
    """Utils to transform multiline strings into single line for better logging.

    Args:
        x: String to be flattened.

    Returns:
        Given string in one line with consecutive space squeezed.
    """
    x = ''.join(x.splitlines())
    x.strip()
    while '  ' in x:
        x = x.replace('  ', ' ')
    return x.strip()
