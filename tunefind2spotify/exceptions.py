"""Definition of custom Exception derivatives."""

import logging


class MissingCredentialsException(Exception):
    pass


class EmptyJSONResponse(Exception):
    pass


class MediaNotFound(Exception):
    pass


def log_and_raise(logger: logging.Logger, exception: BaseException or type, message: str) -> None:
    """Logs a gives message at ERROR level and raises the given exception.

    Args:
        logger: Logger object with which the message will be logged.
        exception: The exception instance (instance of BaseException) or the
            exception type (class) to be raised after logging.
        message: The message to be logged and given to the exception class.
    """
    if isinstance(exception, BaseException):
        logger.error(message)
        raise exception
    else:
        logger.error(message)
        raise exception(message)
