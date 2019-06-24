"""Get typing."""

import types
import typing

from .get_origins import _get_last_origin
from .helpers import (
    LITERAL_TYPES, PY_OLD, TYPING_OBJECTS, get_special_wrapped,
    safe_dict_get, safe_dict_get_both, typing_extensions
)


if PY_OLD:
    def _get_typing(type_):
        origin = _get_last_origin(type_)
        if origin is not None:
            return origin, safe_dict_get(TYPING_OBJECTS.typing, origin) or origin

        if isinstance(type_, typing.GenericMeta):
            return type_, type_
        return None
else:
    def _get_typing(type_):
        origin = getattr(type_, '__origin__', None)
        if origin is not None:
            return safe_dict_get(TYPING_OBJECTS.class_, origin) or origin, origin

        if hasattr(type_, '__orig_bases__'):
            return type_, type_
        return None
_get_typing.__doc__ = """
Return the typing type and class type of a wrapped or unwrapped type.

This function doesn't work special types, these require another function to
extract the information correctly. Builtin {literal types, class types,
typing types} all are handled before this function runs.

.. testsetup::

    from typing_inspect_lib.core.get_typing import _get_typing

.. doctest::

    >>> class MyClass(Generic[TKey, TValue]): pass

    >>> _get_typing(Mapping[str, int])
    (typing.Mapping, <class 'collections.abc.Mapping'>)
    >>> _get_typing(MyClass)
    (<class 'MyClass'>, <class 'MyClass'>)
    >>> _get_typing(MyClass[str, int])
    (<class 'MyClass'>, <class 'MyClass'>)
"""


def _get_special_typing_universal(type_):
    """
    Handle universal types.

    Currently handles the following types:

     - :class:`typing.TypeVar`,
     - :func:`typing.NewType`,
     - :class:`typing_extensions.Protocol`.
    """
    if isinstance(type_, typing.TypeVar):
        return typing.TypeVar, type_
    if isinstance(type_, typing_extensions._ProtocolMeta):
        return typing_extensions.Protocol, type_
    if isinstance(type_, types.FunctionType) and hasattr(type_, '__supertype__'):
        return typing_extensions.NewType, type_
    return None


if PY_OLD:
    def _get_special_typing(type_):
        return get_special_wrapped(type_)
else:
    def _get_special_typing(type_):
        return None
_get_special_typing.__doc__ = """\
Handle special types that can't be handled through normal means."""


def get_typing(type_):
    """
    Get the typing type and the class type of the type passed to it.

    .. doctest::

        >>> get_typing(Mapping)
        (typing.Mapping, <class 'collections.abc.Mapping'>)
        >>> get_typing(Mapping[str, int])
        (typing.Mapping, <class 'collections.abc.Mapping'>)

        # Not all types have different typing and class types.
        >>> get_typing(Union[str, int])
        (typing.Union, typing.Union)

    """
    ret = (
        _get_special_typing_universal(type_)
        or safe_dict_get(LITERAL_TYPES, type_)
        or safe_dict_get_both(TYPING_OBJECTS.class_, type_, inv=True)
        or safe_dict_get_both(TYPING_OBJECTS.typing, type_)
        or _get_typing(type_)
        or _get_special_typing(type_)
    )
    if ret is None:
        return None, None
    type_type, class_type = ret
    if type_type is typing_extensions.NewType:
        class_type = type_
    return type_type, class_type
