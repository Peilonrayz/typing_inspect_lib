"""Builds internal mappings."""

import collections
import json
import operator
import os.path

try:
    import typing_extensions  # noqa: F401 This is used by _read_globals
except ImportError:
    pass

from .compatability import re, abc, typing, typings
from .helpers import PY350_2, PY_OLD, VERSION, safe_dict_get, safe_dict_get_both

__all__ = [
    'LITERAL_TYPES',
    'TYPING_OBJECTS',
    'is_typing',
    'is_special',
    'get_special_wrapped',
]

_SENTINEL = object()

_FILE_DIR = os.path.dirname(__file__)
with open(os.path.join(_FILE_DIR, 'links.json')) as f:
    _LINKS = json.load(f)


if PY_OLD:
    def _from_typing_to_class(t_typing):
        return getattr(t_typing, '__extra__', None) or t_typing
else:
    def _from_typing_to_class(t_typing):
        """Get class type from typing type."""
        return getattr(t_typing, '__origin__', None) or t_typing


class _Types(abc.MutableMapping):
    """Mapping between two types."""

    def __init__(self):
        self._values = {}
        # Should be set to the inverse
        self._inv = {}

    def __getitem__(self, key):
        return self._values[key]

    def __setitem__(self, key, value):
        old_value = self._values.get(key, _SENTINEL)
        if old_value is not _SENTINEL:
            self._inv.pop(old_value, None)
        self._values[key] = value
        self._inv._values[value] = key

    def __delitem__(self, value):
        self._values.__delitem__(value)

    def __len__(self):
        return len(self._values)

    def __iter__(self):
        return iter(self._values)


class Types(object):  # pylint: disable=useless-object-inheritance, too-few-public-methods
    """Hold typing and class conversions."""

    def __init__(self, types):
        self.typing = _Types()
        self.class_ = _Types()
        self.typing._inv = self.class_
        self.class_._inv = self.typing

        for t_typing in types:
            self.typing[t_typing] = _from_typing_to_class(t_typing)

        self.class_to_typing = self.class_
        self.typing_to_class = self.typing


def _literal_to_link_types(literals):
    """Build literal dictionary."""
    return {l: (l, l) for l in literals}


def _read_globals(global_attrs):
    """Read global values and get attributes."""
    global_ = globals()
    values = []
    for attr in global_attrs:
        mod, attr = attr.split('.', 1)
        get = operator.attrgetter(attr)
        try:
            value = get(global_[mod])
        except (AttributeError, KeyError):
            pass
        else:
            values.append(value)
    return values


LITERAL_TYPES = _literal_to_link_types(
    [
        str,
        int,
        bytes,
        type(None),
    ]
    + (
        [unicode]  # noqa: F821, pylint: disable=undefined-variable
        if VERSION < (3, 0, 0) else
        []
    )
    + _read_globals(_LINKS['literal']),
)

TYPING_OBJECTS = Types(_read_globals(_LINKS['typing']))
SPECIAL_OBJECTS = Types(_read_globals(_LINKS['special']))
SPECIAL_OBJECTS_WRAPPED = Types(_read_globals(_LINKS['special wrapped']))

# Edge cases
_CHANGES = [
    (typing.Pattern, re.Pattern),
    (typing.Match, re.Match),
    (typing.Dict, dict),
    (typing.List, list),
    (typing.Set, set),
    (typing.FrozenSet, frozenset),
    (typing.Tuple, tuple),
    (typing.Callable, abc.Callable),
    (typing.AbstractSet, abc.Set),
    (typing.MutableMapping, abc.MutableMapping),
    (typing.MutableSequence, abc.MutableSequence),
    (typing.MutableSet, abc.MutableSet),
]
for from_, to in _CHANGES:
    for mapping in (TYPING_OBJECTS, SPECIAL_OBJECTS, SPECIAL_OBJECTS_WRAPPED):
        if from_ in mapping.typing:
            mapping.typing[from_] = to


_SPECIAL_CONV = {
    (typing.CallableMeta if PY_OLD else collections.abc.Callable):
        SPECIAL_OBJECTS_WRAPPED.typing_to_class[typing.Callable],
    (typings._ClassVarMeta if PY350_2 else typing._ClassVar):
        typings.ClassVar,
    (typing.OptionalMeta if PY350_2 else typing.Optional):
        typing.Optional,
    (typing.TupleMeta if PY_OLD else tuple):
        SPECIAL_OBJECTS_WRAPPED.typing_to_class[typing.Tuple],
    (typing.UnionMeta if PY350_2 else typing._Union):
        typing.Union,
}


def get_special_wrapped(type_):
    """Get special types types."""
    key = safe_dict_get(_SPECIAL_CONV, type(type_), type(type_))
    return safe_dict_get_both(SPECIAL_OBJECTS_WRAPPED.class_, key, inv=True)


def is_typing(type_):
    """Check if type is a :mod:`typing` type."""
    return type_ in TYPING_OBJECTS.typing or type_ in TYPING_OBJECTS.class_


def is_special(type_):
    """Check if type is special type."""
    return type_ in SPECIAL_OBJECTS.typing or type_ in SPECIAL_OBJECTS.class_
