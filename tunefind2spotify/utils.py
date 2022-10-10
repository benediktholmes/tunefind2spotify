"""Collection of project wide utility functions."""

import argparse
import enum

from functools import wraps
from typing import List


def singleton(cls):
    """Decorator that enforces the Singleton pattern for a given class.

    Note:
        Class object as well as its instantiations hold a reference `instance`
        to the first instance of the class created. Method `__new__` is altered
        to store the created instance when it is first called and return this
        instance on consecutive calls.

    Args:
        cls: Class object to be decorated.

    Returns:
        Given class object with altered object creation method `__new__`.
    """
    def func_decorator(func):

        @wraps(func)
        def new(cls, *args, **kwargs):
            if not hasattr(cls, 'instance'):
                setattr(cls, 'instance', None)
            if cls.instance is None:
                cls.instance = func(cls)
            return cls.instance
        return new

    setattr(cls, '__new__', func_decorator(cls.__new__))
    return cls


class MediaType(enum.IntEnum):
    """Enum for ease of handling values describing Tunefind media types."""
    SHOW = 0
    MOVIE = 1
    GAME = 2

    @staticmethod
    def read_in(x: str) -> 'MediaType' or None:
        """Returns MediaType that matches respective string representation."""
        if not isinstance(x, str):
            return None
        else:
            x = x.upper()
            if x in MediaType._member_names_:
                return MediaType[x]
            else:
                return None

    @staticmethod
    def translate(x: 'MediaType') -> str:
        """Returns lowercase string representation of MediaType value."""
        return x.name.lower()


def dict_keep(d: dict, keys: List[object]) -> dict:
    """Keep only the entries in dict `d` specified by given `keys`.

    Note:
        Items that are passed with `keys` but are not present in `d.keys()`
        are ignored. Does not apply filtering to nested dictionaries!

    Args:
        d: Dictionary object to be stripped.
        keys: List of dictionary keys that are retained.

    Returns:
        A new dictionary with at most the keys specified by `keys`.
    """
    return {k: v for k, v in d.items() if k in keys}


class EnumAction(argparse.Action):
    """Argparse action for handling enums."""

    def __init__(self, **kwargs) -> None:
        """Sets type of choices."""
        enum_type = kwargs.pop('type', None)
        if enum_type is None:
            raise ValueError(f'Argument `{type}` must be assigned an enum when using EnumAction')
        if not issubclass(enum_type, enum.Enum):
            raise TypeError(f'Argument `{type}` must be an enum when using EnumAction')

        kwargs.setdefault('choices', tuple(e.name for e in enum_type))

        super(EnumAction, self).__init__(**kwargs)
        self._enum = enum_type

    def __call__(self,
                 parser,
                 namespace,
                 values,
                 option_string=None) -> None:
        """Convert value to enum."""
        value = self._enum[values]
        setattr(namespace, self.dest, value)
