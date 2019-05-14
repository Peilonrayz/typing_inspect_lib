from .get_bases import _BaseObj, get_bases
from ..core import get_type_info


def _get_parents(type_):
    parents = ()
    for base in get_bases(type_):
        parents += (base,)
        parents += _get_parents(base.class_ if base.orig is None else base.orig)
    return parents


def get_parents(type_):
    """Get the parents of the types, returns the typing type, class type and orig type."""
    type_info = get_type_info(type_)
    if type_info is None:
        typing_ = type_
        class_ = type_
        orig = None
    else:
        typing_, class_ = type_info.typing, type_info.class_
        orig = type_ if type_info.args else None
    return (_BaseObj(typing_, class_, orig),) + _get_parents(type_)
