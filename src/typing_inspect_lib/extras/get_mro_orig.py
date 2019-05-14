import typing

from .get_bases import _BaseObj
from .get_mro import get_mro
from .get_parents import get_parents
from ..core import get_args, get_type_info, get_typing
from ..core.helpers import (
    PY_35, VERSION, pairwise, is_typing
)


def _inner_set(values):
    values_ = zip(*values)
    return [set(value) for value in values_]


if PY_35 and VERSION <= (3, 5, 2):
    def _ensure_consumed_parents(type_, parents):
        if parents:
            type_info = get_type_info(type_)
            if is_typing(type_info.class_):
                parents.pop(typing.Generic, None)
                if not parents:
                    return
            raise ValueError("Didn't consume all parents: {0}".format(parents))
else:
    def _ensure_consumed_parents(type_, parents):
        if parents:
            raise ValueError("Didn't consume all parents: {0}".format(parents))


def get_mro_orig(type_):
    """
    Gets the mro of the type. Returning them as typing types, class types and orig types.

    Builtin types are converted to their class type to get the MRO
    and so `Generic` is missing.
    """
    parents = {}
    for parent in get_parents(type_):
        parents.setdefault(parent.class_, []).append(parent)

    mro = ()
    for class_ in get_mro(type_):
        if class_ not in parents:
            t, c = get_typing(class_)
            mro += (_BaseObj(t or class_, c or class_, None),)
            continue

        classes = parents.pop(class_)
        if not all(a.typing is b.typing for a, b in pairwise(classes)):
            raise ValueError('MRO has two different types using the same class')

        if all(c.orig is None for c in classes):
            mro += (classes[0],)
            continue

        args = _inner_set(get_args(c.orig) if c.orig is not None else {} for c in classes)
        new_args = ()
        for arg in args:
            if not args:
                raise ValueError('One argument is empty')
            if len(arg) == 1:
                new_args += (arg.pop(),)
            else:
                new_args += (typing.Union[tuple(arg)],)
        class__ = classes[0]
        mro += (_BaseObj(class__.typing, class__.class_, class__.typing[new_args]),)

    _ensure_consumed_parents(type_, parents)

    return mro
