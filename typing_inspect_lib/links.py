import collections
import typing
import sys
import operator
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

    'CLASS_TYPES',
    'CLASS_TO_TYPING',
    'TYPING_TYPES',
    'TYPING_TO_CLASS',

    'SP_CLASS_TYPES',
    'SP_CLASS_TO_TYPING',
    'SP_TYPING_TYPES',
    'SP_TYPING_TO_CLASS',

    'SP_CLASS_TYPES_WRAPPED',
    'SP_CLASS_TO_TYPING_WRAPPED',
    'SP_TYPING_TYPES_WRAPPED',
    'SP_TYPING_TO_CLASS_WRAPPED',
]

VERSION = sys.version_info[:3]
PY_OLD = VERSION < (3, 7, 0)
PY_35 = VERSION[:2] == (3, 5)

_SENTINEL = object()


class LinkTypes(object):
    def __init__(self, mapping):
        self._mapping = mapping

    def __contains__(self, key):
        try:
            contains = key in self._mapping
        except TypeError:
            return False
        else:
            return contains

    def __getitem__(self, key):
        try:
            value = self._mapping.get(key, _SENTINEL)
        except TypeError:
            return None
        else:
            if value is _SENTINEL:
                return None
            return value


def _literal_to_link_types(literals):
    return LinkTypes({l: (l, l) for l in literals})


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


# Python 3.5 class type incompatibilities
_OLD_CLASS = {
    (typing.Dict, abc.MutableMapping): dict,
    (typing.List, abc.MutableSequence): list,
    (typing.Set, abc.MutableSet): set,
    (typing.FrozenSet, abc.Set): frozenset,
    (typing.Tuple, typing.Tuple): tuple,
    (typing.Callable, typing.Callable): abc.Callable
}


if PY_35 and VERSION <= (3, 5, 1):
    def _from_typing_to_class(t_typing):
        t_class = getattr(t_typing, '__extra__', None) or t_typing
        return _OLD_CLASS.get((t_typing, t_class), t_class)
elif PY_OLD:
    def _from_typing_to_class(t_typing):
        return getattr(t_typing, '__extra__', None) or t_typing
else:
    def _from_typing_to_class(t_typing):
        return getattr(t_typing, '__origin__', None) or t_typing


def _add_typing_class(typings):
    return [
        (t, _from_typing_to_class(t))
        for t in typings
    ]


def _typing_to_link_types(typings):
    return (
        LinkTypes({c: (t, c) for t, c in typings}),
        LinkTypes({c: t for t, c in typings}),
        LinkTypes({t: (t, c) for t, c in typings}),
        LinkTypes({t: c for t, c in typings})
    )


def _add_key_to_link_types(new_key, old_key, *link_types):
    for link_type in link_types:
        try:
            value = link_type._mapping[old_key]
        except KeyError:
            pass
        else:
            link_type._mapping[new_key] = value


def _add_keys_to_link_types(keys, *link_types):
    for key in keys:
        _add_key_to_link_types(*key + link_types)


LITERAL_TYPES = _literal_to_link_types(
    [
        str,
        int,
        bytes,
        type(None),
    ]
    + ([unicode] if VERSION < (3, 0, 0) else [])
    + _read_globals([
        'typing.Any',
        'typing.AnyStr',
        'typing.NoReturn',
        'typing.Text',
        'typing_extensions.NoReturn',
        'typing_extensions.Text',
    ])
)

_TYPING_OBJECTS = _read_globals([
    # Special
    'typing.Callable',
    'typing.ClassVar',
    'typing.Generic',
    'typing.Optional',
    'typing.Tuple',
    'typing.Type',
    'typing.Union',
    'typing_extensions.Protocol',
    'typing_extensions.ClassVar',
    'typing_extensions.Type',

    # ABC
    'typing.AbstractSet',
    'typing.ByteString',
    'typing.Container',
    'typing.ContextManager',
    'typing.Hashable',
    'typing.ItemsView',
    'typing.Iterable',
    'typing.Iterator',
    'typing.KeysView',
    'typing.Mapping',
    'typing.MappingView',
    'typing.MutableMapping',
    'typing.MutableSequence',
    'typing.MutableSet',
    'typing.Sequence',
    'typing.Sized',
    'typing.ValuesView',
    'typing.Awaitable',
    'typing.AsyncIterator',
    'typing.AsyncIterable',
    'typing.Coroutine',
    'typing.Collection',
    'typing.AsyncGenerator',
    'typing.AsyncContextManager',
    'typing_extensions.ContextManager',
    'typing_extensions.Awaitable',
    'typing_extensions.AsyncIterator',
    'typing_extensions.AsyncIterable',
    'typing_extensions.Coroutine',
    'typing_extensions.AsyncGenerator',
    'typing_extensions.AsyncContextManager',

    # Protocols
    'typing.Reversible',
    'typing.SupportsAbs',
    'typing.SupportsBytes',
    'typing.SupportsComplex',
    'typing.SupportsFloat',
    'typing.SupportsInt',
    'typing.SupportsRound',

    # Collection
    'typing.Counter',
    'typing.ChainMap',
    'typing.Deque',
    'typing.Dict',
    'typing.DefaultDict',
    'typing.List',
    'typing.Set',
    'typing.FrozenSet',
    'typing.NamedTuple',  # TODO: check
    'typing.OrderedDict',
    'typing.Generator',
    'typing_extensions.ChainMap',
    'typing_extensions.Counter',
    'typing_extensions.Deque',
    'typing_extensions.DefaultDict',

    # One Off
    'typing.NewType',  # TODO: check
    'typing_extensions.NewType',
])
(
    CLASS_TYPES,
    CLASS_TO_TYPING,
    TYPING_TYPES,
    TYPING_TO_CLASS
) = _typing_to_link_types(_add_typing_class(_TYPING_OBJECTS))

_SPECIAL_OBJECTS = _read_globals([
    'typing.Callable',
    'typing.ClassVar',
    'typing.Generic',
    'typing.NamedTuple',
    'typing.Optional',
    'typing.Tuple',
    'typing.Type',
    'typing.Union',
    'typing_extensions.Protocol',
    'typing_extensions.ClassVar',
    'typing_extensions.Type',
])
(
    SP_CLASS_TYPES,
    SP_CLASS_TO_TYPING,
    SP_TYPING_TYPES,
    SP_TYPING_TO_CLASS
) = _typing_to_link_types(_add_typing_class(_SPECIAL_OBJECTS))

# TODO: ensure this can be removed
if False:
    _add_keys_to_link_types(
        [
            (typing_._ClassVar, typing_.ClassVar),
            (typing_._Union, typing.Union)
        ],
        SP_CLASS_TYPES, SP_CLASS_TO_TYPING
    )

_SPECIAL_OBJECTS_WRAPPED = _read_globals([
    'typing.Callable',
    'typing.ClassVar',
    'typing.Generic',
    'typing.Optional',
    'typing.Tuple',
    'typing.Union',
    'typing_extensions.ClassVar',
])
(
    SP_CLASS_TYPES_WRAPPED,
    SP_CLASS_TO_TYPING_WRAPPED,
    SP_TYPING_TYPES_WRAPPED,
    SP_TYPING_TO_CLASS_WRAPPED
) = _typing_to_link_types(_add_typing_class(_SPECIAL_OBJECTS_WRAPPED))

_PY350_2 = PY_35 and VERSION < (3, 5, 2)

_add_keys_to_link_types(
    [
        ((typing.CallableMeta if PY_OLD else collections.abc.Callable), SP_TYPING_TO_CLASS_WRAPPED[typing.Callable]),
        ((typing_.ClassVarMeta if _PY350_2 else typing_._ClassVar), typing_.ClassVar),
        ((typing.OptionalMeta if _PY350_2 else typing.Optional), typing.Optional),
        ((typing.TupleMeta if PY_OLD else tuple), SP_TYPING_TO_CLASS_WRAPPED[typing.Tuple]),
        ((typing.UnionMeta if _PY350_2 else typing_._Union), typing.Union),
    ],
    SP_CLASS_TYPES_WRAPPED, SP_CLASS_TO_TYPING_WRAPPED
)
