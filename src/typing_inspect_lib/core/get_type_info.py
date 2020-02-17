"""Get type info."""

import collections

from .get_args import _get_args
from .get_parameters import _get_parameters
from .get_typing import get_typing


TypeInfo = collections.namedtuple(
    'TypeInfo',
    ['unwrapped', 'origin', 'original', 'args', 'parameters'],
)
_TypeInfo = TypeInfo


def get_type_info(type_):
    """
    Get all the type information for a type.

    .. doctest::

        >>> type_ = get_type_info(Mapping[TKey, int])
        >>> type_
        TypeInfo(typing=typing.Mapping, class_=<class 'collections.abc.Mapping'>, args=(~TKey, <class 'int'>), parameters=(~TKey,))
        >>> type_.unwrapped
        typing.Mapping
        >>> type_.class_
        <class 'collections.abc.Mapping'>
        >>> type_.args
        (~TKey, <class 'int'>)
        >>> type_.parameters
        (~TKey,)
    """
    u_type, o_type = get_typing(type_)
    if u_type is None and o_type is None:
        return None
    args = tuple(a for a in _get_args(type_, t_typing=u_type))
    parameters = tuple(p for p in _get_parameters(type_, t_typing=u_type))
    return TypeInfo(u_type, o_type, type_, args, parameters)
