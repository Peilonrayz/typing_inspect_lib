"""Get MRO orig."""

import typing

from .get_bases import _BaseObj
from .get_mro import get_mro
from .get_parents import get_parents
from ..core import get_args, get_type_info, get_typing
from ..core.helpers import helpers, links


def _inner_set(values):
    """Get the set of values in tables columns."""
    values_ = zip(*values)
    return [set(value) for value in values_]


if helpers.PY_35 and helpers.VERSION <= (3, 5, 2):
    def _ensure_consumed_parents(type_, parents):
        if parents:
            type_info = get_type_info(type_)
            if links.is_typing(type_info.origin):
                parents.pop(typing.Generic, None)
                if not parents:
                    return
            raise ValueError("Didn't consume all parents: {0}".format(parents))
else:
    def _ensure_consumed_parents(type_, parents):
        """Ensure all parents have been consumed."""
        if parents:
            raise ValueError("Didn't consume all parents: {0}".format(parents))


def get_mro_orig(type_):
    """
    Get the mro of the type. Returning them as typing types, class types and orig types.

    Builtin types are converted to their class type to get the MRO
    and so :class:`typing.Generic` is missing.
    """
    parents = {}
    for parent in get_parents(type_):
        parents.setdefault(parent.origin, []).append(parent)

    mro = ()
    for o_type in get_mro(type_):
        if o_type not in parents:
            u_type, o_type_ = get_typing(o_type)
            mro += (_BaseObj(u_type or o_type, o_type_ or o_type, None),)
            continue

        classes = parents.pop(o_type)
        if not all(a.unwrapped is b.unwrapped for a, b in helpers.pairwise(classes)):
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
        class_ = classes[0]
        mro += (_BaseObj(class_.unwrapped, class_.origin, class_.unwrapped[new_args]),)

    _ensure_consumed_parents(type_, parents)

    return mro
