import typing

from ..core.helpers import PY_35, VERSION, TYPING_OBJECTS, safe_dict_contains, safe_dict_get, pairwise

from ..core import get_type_info, get_args

from .get_mro import get_mro
from .get_bases import _BaseObj
from .get_parents import get_parents


def _inner_set(values):
    vs = zip(*values)
    return [set(v) for v in vs]


if PY_35 and VERSION <= (3, 5, 2):
    def _ensure_consumed_parents(type_, parents):
        if parents:
            type_info = get_type_info(type_)
            if safe_dict_contains(TYPING_OBJECTS.class_types, type_info.class_):
                parents.pop(typing.Generic, None)
                if not parents:
                    return
            raise ValueError("Didn't consume all parents: {}".format(parents))
else:
    def _ensure_consumed_parents(type_, parents):
        if parents:
            raise ValueError("Didn't consume all parents: {}".format(parents))


def get_mro_orig(type_):
    """
    Gets the mro of the type. Returning them as typing types, class types and orig types.

    Builtin types are converted to their class type to get the MRO and so `Generic` is missing.
    """
    parents = {}
    for parent in get_parents(type_):
        parents.setdefault(parent.class_, []).append(parent)

    mro = ()
    for class_ in get_mro(type_):
        if class_ not in parents:
            mro += _BaseObj(safe_dict_get(TYPING_OBJECTS.class_to_typing, class_) or class_, class_, None),
            continue

        classes = parents.pop(class_)
        if not all(a.typing is b.typing for a, b in pairwise(classes)):
            raise ValueError('MRO has two different types using the same class')

        if all(c.orig is None for c in classes):
            mro += classes[0],
            continue

        args = _inner_set(get_args(c.orig) if c.orig is not None else {} for c in classes)
        new_args = ()
        for arg in args:
            if not args:
                raise ValueError('One argument is empty')
            if len(arg) == 1:
                new_args += arg.pop(),
            else:
                new_args += typing.Union[tuple(arg)],
        c = classes[0]
        mro += _BaseObj(c.typing, c.class_, c.typing[new_args]),

    _ensure_consumed_parents(type_, parents)

    return mro
