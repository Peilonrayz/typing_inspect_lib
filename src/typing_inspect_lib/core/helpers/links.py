import collections
import json
import operator
import os.path
import typing

try:
    import typing_extensions  # noqa: F401 This is used by _read_globals
except ImportError:
    pass

from . import abc
from . import typing_
from . import re
from .helpers import PY350_2, PY_35, PY_OLD, VERSION

__all__ = [
    'LITERAL_TYPES',
    'TYPING_OBJECTS',
    'SPECIAL_OBJECTS',
    'SPECIAL_OBJECTS_WRAPPED',
]

_SENTINEL = object()

_FILE_DIR = os.path.dirname(__file__)
with open(os.path.join(_FILE_DIR, 'links.json')) as f:
    _LINKS = json.load(f)


# TODO: move down to edge-cases
# Python 3.5 class type incompatibilities
_OLD_CLASS = {
    (typing.Dict, abc.MutableMapping): dict,
    (typing.List, abc.MutableSequence): list,
    (typing.Set, abc.MutableSet): set,
    (typing.FrozenSet, abc.Set): frozenset,
    (typing.Tuple, typing.Tuple): tuple,
    (typing.Callable, typing.Callable): abc.Callable,
}


if PY_35 and VERSION <= (3, 5, 2):
    def _from_typing_to_class(t_typing):
        t_class = getattr(t_typing, '__extra__', None) or t_typing
        return _OLD_CLASS.get((t_typing, t_class), t_class)
elif PY_OLD:
    def _from_typing_to_class(t_typing):
        return getattr(t_typing, '__extra__', None) or t_typing
else:
    def _from_typing_to_class(t_typing):
        return getattr(t_typing, '__origin__', None) or t_typing


class _TypesBoth(abc.MutableMapping):
    def __init__(self, values, both):
        self._values = values
        self._both = both

    def __getitem__(self, key):
        value = self._values[key]
        return self._both(self._values._inv[value], value)

    def __setitem__(self, key, values):
        if key not in values:
            raise ValueError('Key must be in value')
        if len(values) != 2:
            raise ValueError('Value must have a length of two')
        self._values[key] = [i for i in values if i != key][0]

    def __delitem__(self, v):
        self._values.__delitem__(v)

    def __len__(self):
        return len(self._values)

    def __iter__(self):
        return iter(self._values)


class _Types(abc.MutableMapping):
    def __init__(self, both):
        self._values = {}
        self.both = _TypesBoth(self, both)
        # Should be set to the inverse
        self._inv = {}

    def __getitem__(self, key):
        return self._values[key]

    def __setitem__(self, key, value):
        old_value = self._values.get(key, _SENTINEL)
        if old_value is not _SENTINEL:
            self._inv.pop(old_value)
        self._values[key] = value
        self._inv._values[value] = key

    def __delitem__(self, v):
        self._values.__delitem__(v)

    def __len__(self):
        return len(self._values)

    def __iter__(self):
        return iter(self._values)


class Types(object):  # pylint: disable=useless-object-inheritance, too-few-public-methods
    def __init__(self, types):
        self.typing = _Types(lambda a, b: (a, b))
        self.class_ = _Types(lambda a, b: (b, a))
        self.typing._inv = self.class_
        self.class_._inv = self.typing

        for t in types:
            self.typing[t] = _from_typing_to_class(t)

        self.class_types = self.class_.both
        self.class_to_typing = self.class_
        self.typing_types = self.typing.both
        self.typing_to_class = self.typing
        self._build_class_types()

    def _build_class_types(self):
        # ClassVar only works correctly with this...
        self.class_types = {c: (t, c) for c, t in self.class_.items()}

    @staticmethod
    def _update_class_type(old_key, new_key):
        link_types = (
            SPECIAL_OBJECTS_WRAPPED.class_types,
            # SPECIAL_OBJECTS_WRAPPED.class_to_typing,
        )
        for link_type in link_types:
            try:
                value = link_type[old_key]
            except KeyError:
                pass
            else:
                link_type[new_key] = value

    def update_class_types(self, changes):
        for key in changes:
            self._update_class_type(*key)


def _literal_to_link_types(literals):
    return {l: (l, l) for l in literals}


def _read_globals(global_attrs):
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

TYPING_OBJECTS.typing[typing.Pattern] = re.Pattern
TYPING_OBJECTS.typing[typing.Match] = re.Match
TYPING_OBJECTS._build_class_types()

# TODO: Convert to easier to understand code
SPECIAL_OBJECTS_WRAPPED.update_class_types([
    (
        SPECIAL_OBJECTS_WRAPPED.typing_to_class[typing.Callable],
        (typing.CallableMeta if PY_OLD else collections.abc.Callable),
    ),
    (
        typing_.ClassVar,
        (typing_.ClassVarMeta if PY350_2 else typing_._ClassVar)
    ),
    (
        typing.Optional,
        (typing.OptionalMeta if PY350_2 else typing.Optional)
    ),
    (
        SPECIAL_OBJECTS_WRAPPED.typing_to_class[typing.Tuple],
        (typing.TupleMeta if PY_OLD else tuple)
    ),
    (
        typing.Union,
        (typing.UnionMeta if PY350_2 else typing_._Union)
    ),
])
