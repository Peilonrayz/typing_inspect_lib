"""
In charge of getting the :ref:`Unwrapped` type and :ref:`Origin` type
from any type.

Most functions handle a specific subtype, resulting in either the wanted
types, or :code:`None`.

:func:`typing_inspect_lib.get_typing` lazily calls the functions from
the top down. This means if a :ref:`Literal` type is passed then
:code:`_handle_origin_typing_type` won't be called.
"""

import types
import typing

from .get_origins import _get_last_origin
from .helpers import compatibility, helpers, links


def _handle_special_typing_universal(s_type):
    """
    Handle some :ref:`Special` types.

    Currently handles the following types:

     - :class:`typing.TypeVar`,
     - :func:`typing.NewType`,
     - :class:`typing_extensions.Protocol`.

    .. testsetup::

        from typing_inspect_lib.core.get_typing import (
            _handle_special_typing_universal
        )

    .. testcode::

        assert _handle_special_typing_universal(TKey) == (TypeVar, TKey)

        Example = NewType('Example', int)
        assert _handle_special_typing_universal(Example) == (NewType, Example)
    """
    if isinstance(s_type, typing.TypeVar):
        return typing.TypeVar, s_type
    if isinstance(s_type, compatibility.typing_extensions._ProtocolMeta):
        return compatibility.typing_extensions.Protocol, s_type
    if isinstance(s_type, types.FunctionType) and hasattr(s_type, '__supertype__'):
        return compatibility.typings.NewType, s_type
    return None


def _handle_literal_type(l_type):
    """
    Handle :ref:`Literal` types.

    .. testsetup::

        from typing_inspect_lib.core.get_typing import (
            _handle_literal_type
        )

    .. testcode::

        assert _handle_literal_type(str) == (str, str)
        assert _handle_literal_type(list) == (list, list)
        assert _handle_literal_type(dict) == (dict, dict)
    """
    if links.is_literal(l_type):
        return l_type, l_type
    return None


def _handle_origin_typing_type(o_type):
    """
    Handle :ref:`Origin` :ref:`Typing` types.

    .. testsetup::

        from typing_inspect_lib.core.get_typing import (
            _handle_origin_typing_type
        )

    .. testcode::

        assert (_handle_origin_typing_type(abc.Mapping)
                == (Mapping, abc.Mapping))
        assert (_handle_origin_typing_type(abc.Sequence)
                == (Sequence, abc.Sequence))
    """
    return links.get_typing_from_class(o_type)


def _handle_unwrapped_typing_type(ut_type):
    """
    Handle :ref:`Unwrapped` :ref:`Typing` types.

    .. testsetup::

        from typing_inspect_lib.core.get_typing import (
            _handle_unwrapped_typing_type
        )

    .. testcode::

        assert (_handle_unwrapped_typing_type(Mapping)
                == (Mapping, abc.Mapping))
        assert (_handle_unwrapped_typing_type(Sequence)
                == (Sequence, abc.Sequence))
    """
    return links.get_typing_from_typing(ut_type)


if helpers.PY_OLD:
    def _handle_typing(type_):
        origin = _get_last_origin(type_)
        if origin is not None:
            return origin, links.get_type_from_typing(origin) or origin

        if isinstance(type_, typing.GenericMeta):
            return type_, type_
        return None
else:
    def _handle_typing(type_):
        origin = getattr(type_, '__origin__', None)
        if origin is not None:
            return links.get_type_from_class(origin) or origin, origin

        if hasattr(type_, '__orig_bases__'):
            return type_, type_
        return None
_handle_typing.__doc__ = """
Handle :ref:`Wrapped` :ref:`Typing` types and :ref:`User Defined` types.

.. testsetup::

    from typing_inspect_lib.core.get_typing import _handle_typing

.. testcode::

    class MyClass(Generic[TKey, TValue]):
        pass

    assert _handle_typing(Mapping[str, int]) == (Mapping, abc.Mapping)
    assert _handle_typing(MyClass) == (MyClass, MyClass)
    assert _handle_typing(MyClass[str, int]) == (MyClass, MyClass)
"""


def _handle_special_typing(s_type):
    """Handle :ref:`Special` types."""
    return links.get_special(s_type)


def get_typing(type_):
    """
    Get the :ref:`Unwrapped` type and the :ref:`Origin` type from type.

    .. testcode::

        assert get_typing(Mapping) == (Mapping, abc.Mapping)
        assert get_typing(Mapping[str, int]) == (Mapping, abc.Mapping)

        # Not all types have different typing and class types.
        assert get_typing(Union[str, int]) == (Union, Union)
    """
    ret = (
        _handle_special_typing_universal(type_)
        or _handle_literal_type(type_)
        or _handle_origin_typing_type(type_)
        or _handle_unwrapped_typing_type(type_)
        or _handle_typing(type_)
        or _handle_special_typing(type_)
    )
    if ret is None:
        return None, None
    unwrapped_type, origin_type = ret
    if unwrapped_type is compatibility.typing_extensions.NewType:
        origin_type = type_
    return unwrapped_type, origin_type
