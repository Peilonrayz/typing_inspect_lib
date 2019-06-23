"""Get type info."""

import collections

from .get_args import _get_args
from .get_parameters import _get_parameters
from .get_typing import get_typing


_TypeInfo = collections.namedtuple(
    'TypeInfo',
    ['typing', 'class_', 'args', 'parameters'],
)


def get_type_info(type_):
    """
    Get all the type information for a type.

    .. doctest::

        >>> type_ = get_type_info(Mapping[TKey, int])
        >>> type_
        TypeInfo(typing=typing.Mapping, class_=<class 'collections.abc.Mapping'>, args=(~TKey, <class 'int'>), parameters=(~TKey,))
        >>> type_.typing
        typing.Mapping
        >>> type_.class_
        <class 'collections.abc.Mapping'>
        >>> type_.args
        (~TKey, <class 'int'>)
        >>> type_.parameters
        (~TKey,)
    """
    t_typing, class_ = get_typing(type_)
    if t_typing is None and class_ is None:
        return None
    args = tuple(a for a in _get_args(type_, t_typing=t_typing))
    parameters = tuple(p for p in _get_parameters(type_, t_typing=t_typing))
    return _TypeInfo(t_typing, class_, args, parameters)
