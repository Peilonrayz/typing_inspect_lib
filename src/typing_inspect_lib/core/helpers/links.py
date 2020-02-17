"""Builds internal mappings."""

import collections

from . import compatibility
from . import helpers

__all__ = [
    'is_literal',
    'is_typing',
    'is_special',
    'get_special',
    'get_typing_from_typing',
    'get_typing_from_class',
    'get_type_from_typing',
    'get_type_from_class',
]

LITERAL_TYPES = set(
    [
        str,
        int,
        bytes,
        type(None),
        list,
        dict,
    ]
    + (
        [unicode]  # noqa: F821, pylint: disable=undefined-variable
        if helpers.VERSION < (3, 0, 0) else
        []
    )
)

TYPING_OBJECTS = helpers.Types(
    helpers.get_typings(compatibility.typing, compatibility.typing_extensions)
    # Add non-generic non protocol types from typing & typing_extensions
    + [
        compatibility.typing.Callable,
        compatibility.typing.Generic,
        compatibility.typing.Optional,
        compatibility.typing.Union,
        compatibility.typing.ClassVar,
        compatibility.typing.NamedTuple,
        compatibility.typing.NewType,
        compatibility.typing.Any,
        compatibility.typing.AnyStr,
        compatibility.typing.NoReturn,
        compatibility.typing.Hashable,
        compatibility.typing.Sized,
        compatibility.typing.Pattern,
        compatibility.typing.Match,
        compatibility.typing_extensions.ClassVar,
        compatibility.typing_extensions.NewType,
        compatibility.typing_extensions.NoReturn,
    ]
)
SPECIAL_OBJECTS = helpers.Types([
    compatibility.typing.Callable,
    compatibility.typing.Generic,
    compatibility.typing.Optional,
    compatibility.typing.Union,
    compatibility.typing.ClassVar,
    compatibility.typing.Tuple,
    compatibility.typing_extensions.ClassVar
])

# Edge cases - Normalize output in all Python versions.
_CHANGES = [
    (compatibility.typing.Pattern, compatibility.re.Pattern),
    (compatibility.typing.Match, compatibility.re.Match),
    (compatibility.typing.Dict, dict),
    (compatibility.typing.List, list),
    (compatibility.typing.Set, set),
    (compatibility.typing.FrozenSet, frozenset),
    (compatibility.typing.Tuple, tuple),
    (compatibility.typing.Callable, compatibility.abc.Callable),
    (compatibility.typing.AbstractSet, compatibility.abc.Set),
    (compatibility.typing.MutableMapping, compatibility.abc.MutableMapping),
    (compatibility.typing.MutableSequence, compatibility.abc.MutableSequence),
    (compatibility.typing.MutableSet, compatibility.abc.MutableSet),
]
for from_, to in _CHANGES:
    for mapping in (TYPING_OBJECTS, SPECIAL_OBJECTS):
        if from_ in mapping.typing:
            mapping.typing[from_] = to


_SPECIAL_CONV = {
    (compatibility.typing.CallableMeta if helpers.PY_OLD else collections.abc.Callable):
        SPECIAL_OBJECTS.typing_to_class[compatibility.typing.Callable],
    (compatibility.typings._ClassVarMeta if helpers.PY350_2 else compatibility.typing._ClassVar):
        compatibility.typings.ClassVar,
    (compatibility.typing.OptionalMeta if helpers.PY350_2 else compatibility.typing.Optional):
        compatibility.typing.Optional,
    (compatibility.typing.TupleMeta if helpers.PY_OLD else tuple):
        SPECIAL_OBJECTS.typing_to_class[compatibility.typing.Tuple],
    (compatibility.typing.UnionMeta if helpers.PY350_2 else compatibility.typing._Union):
        compatibility.typing.Union,
}


def is_literal(type_):
    """Check if type is a :ref:`Literal` type."""
    return helpers.safe_contains(LITERAL_TYPES, type_)


def is_typing(type_):
    """Check if type is a :ref:`Typing` type."""
    return (
        helpers.safe_contains(TYPING_OBJECTS.typing, type_)
        or helpers.safe_contains(TYPING_OBJECTS.class_, type_)
    )


def is_special(type_):
    """Check if type is a :ref:`Special` type."""
    return type_ in SPECIAL_OBJECTS.typing or type_ in SPECIAL_OBJECTS.class_


def get_special(type_):
    """
    Convert from :ref:`Special` type.

    Converts to :ref:`Unwrapped` and :ref:`Origin` types.
    """
    key = helpers.safe_dict_get(_SPECIAL_CONV, type(type_), type(type_))
    return helpers.safe_dict_get_both(SPECIAL_OBJECTS.class_, key, inv=True)


def get_typing_from_typing(type_):
    """
    Convert from :ref:`Wrapped`/:ref:`Unwrapped` :ref:`Typing` type.

    Converts to :ref:`Unwrapped` and :ref:`Origin` type.
    """
    return helpers.safe_dict_get_both(TYPING_OBJECTS.typing, type_)


def get_typing_from_class(type_):
    """
    Convert from :ref:`Class` :ref:`Typing` type.

    Converts to :ref:`Unwrapped` and :ref:`Origin` type.
    """
    return helpers.safe_dict_get_both(TYPING_OBJECTS.class_, type_, inv=True)


def get_type_from_typing(type_):
    """
    Convert from :ref:`Wrapped`/:ref:`Unwrapped` :ref:`Typing` type.

    Converts to :ref:`Origin` type.
    """
    return helpers.safe_dict_get(TYPING_OBJECTS.typing, type_)


def get_type_from_class(type_):
    """
    Convert from :ref:`Origin` :ref:`Typing` type.

    Converts to :ref:`Unwrapped` type.
    """
    return helpers.safe_dict_get(TYPING_OBJECTS.class_, type_)
