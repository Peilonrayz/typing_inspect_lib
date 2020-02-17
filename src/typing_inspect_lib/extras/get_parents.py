"""Get parents."""

from .get_bases import _BaseObj, get_bases
from ..core import get_type_info


def _get_parents(type_):
    """Get the parents from the provided type."""
    parents = ()
    for base in get_bases(type_):
        parents += (base,)
        parents += _get_parents(base.origin if base.orig is None else base.orig)
    return parents


def get_parents(type_):
    """Get the parents of the types, returns the typing type, class type and orig type."""
    type_info = get_type_info(type_)
    if type_info is None:
        u_type = type_
        o_type = type_
        orig = None
    else:
        u_type, o_type = type_info.unwrapped, type_info.origin
        orig = type_ if type_info.args else None
    return (_BaseObj(u_type, o_type, orig),) + _get_parents(type_)
