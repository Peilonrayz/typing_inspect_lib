import collections
import typing
import sys
import operator
import json
import os.path

try:
    import typing_extensions
except ImportError:
    pass

from ._compat import typing_, abc


__all__ = [
    'VERSION',
    'PY_OLD',
    'PY_35',
    'LITERAL_TYPES',
    'TYPING_OBJECTS',
    'SPECIAL_OBJECTS',
    'SPECIAL_OBJECTS_WRAPPED',
]

VERSION = sys.version_info[:3]
PY_OLD = VERSION < (3, 7, 0)
PY_35 = VERSION[:2] == (3, 5)
_PY350_2 = PY_35 and VERSION <= (3, 5, 2)

_SENTINEL = object()

_FILE_DIR = os.path.dirname(__file__)
with open(os.path.join(_FILE_DIR, 'links.json')) as f:
    _LINKS = json.load(f)


# Python 3.5 class type incompatibilities
_OLD_CLASS = {
    (typing.Dict, abc.MutableMapping): dict,
    (typing.List, abc.MutableSequence): list,
    (typing.Set, abc.MutableSet): set,
    (typing.FrozenSet, abc.Set): frozenset,
    (typing.Tuple, typing.Tuple): tuple,
    (typing.Callable, typing.Callable): abc.Callable
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


class Types(object):
    def __init__(self, types):
        typings = [
            (t, _from_typing_to_class(t))
            for t in types
        ]
        self.class_types = {c: (t, c) for t, c in typings}
        self.class_to_typing = {c: t for t, c in typings}
        self.typing_types = {t: (t, c) for t, c in typings}
        self.typing_to_class = {t: c for t, c in typings}

    @staticmethod
    def _update_class_type(old_key, new_key):
        link_types = SPECIAL_OBJECTS_WRAPPED.class_types, SPECIAL_OBJECTS_WRAPPED.class_to_typing
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
            v = get(global_[mod])
        except (AttributeError, KeyError):
            pass
        else:
            values.append(v)
    return values


LITERAL_TYPES = _literal_to_link_types(
    [
        str,
        int,
        bytes,
        type(None),
    ]
    + ([unicode] if VERSION < (3, 0, 0) else [])
    + _read_globals(_LINKS['literal'])
)

TYPING_OBJECTS = Types(_read_globals(_LINKS['typing']))
SPECIAL_OBJECTS = Types(_read_globals(_LINKS['special']))
SPECIAL_OBJECTS_WRAPPED = Types(_read_globals(_LINKS['special wrapped']))

SPECIAL_OBJECTS_WRAPPED.update_class_types([
    (SPECIAL_OBJECTS_WRAPPED.typing_to_class[typing.Callable], (typing.CallableMeta if PY_OLD else collections.abc.Callable)),
    (typing_.ClassVar, (typing_.ClassVarMeta if _PY350_2 else typing_._ClassVar)),
    (typing.Optional, (typing.OptionalMeta if _PY350_2 else typing.Optional)),
    (SPECIAL_OBJECTS_WRAPPED.typing_to_class[typing.Tuple], (typing.TupleMeta if PY_OLD else tuple)),
    (typing.Union, (typing.UnionMeta if _PY350_2 else typing_._Union)),
])
