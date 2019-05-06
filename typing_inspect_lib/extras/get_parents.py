from ..core.helpers import TYPING_OBJECTS, safe_dict_get

from ..core import get_type_info
from .get_bases import _BaseObj, get_bases


def _get_parents(type_):
    parents = ()
    for base in get_bases(type_):
        parents += base,
        b = base.class_ if base.orig is None else base.orig
        parents += _get_parents(b)
    return parents


def get_parents(type_):
    """Gets the parents of the types, returns the typing type, class type and orig type."""
    t = get_type_info(type_)
    if t is None:
        typing_ = safe_dict_get(TYPING_OBJECTS.class_to_typing, type_, type_)
        class_ = safe_dict_get(TYPING_OBJECTS.typing_to_class, type_, type_)
        orig = None
    else:
        typing_, class_ = t.typing, t.class_
        orig = type_ if t.args else None
    return (_BaseObj(typing_, class_, orig),) + _get_parents(type_)