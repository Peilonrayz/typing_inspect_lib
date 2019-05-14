from ..core import get_typing
from ..core.helpers import (
    PY_35, PY_OLD, VERSION, safe_getattr_tuple
)


def _get_mro_conv_dedupe(mro):
    collection_mro = iter(
        get_typing(obj)[1] or obj
        for obj in reversed(mro)
    )
    mro = ()
    mro_set = set()
    for obj in collection_mro:
        if obj not in mro_set:
            mro_set.add(obj)
            mro += (obj,)
    return tuple(reversed(mro))


def _from_types(types, index=1):
    mro = ()
    for type_ in types:
        typing = get_typing(type_)[index]
        mro += (type_ if typing is None else typing,)
    return mro


if PY_35 and VERSION <= (3, 5, 2):
    def _get_mro(type_):
        return _get_mro_conv_dedupe(_from_types(safe_getattr_tuple(type_, '__mro__')))
elif PY_OLD:
    def _get_mro(type_):
        return _get_mro_conv_dedupe(safe_getattr_tuple(type_, '__mro__'))
else:
    def _get_mro(type_):
        return safe_getattr_tuple(type_, '__mro__')


def get_mro(type_):
    """
    Gets the mro of the type. Returning them as class types.

    Builtin types are converted to their class type to get the MRO
    and so `Generic` is missing.

    Example:

        mro = (
            abc.Mapping,
            abc.Collection,
            abc.Sized,
            abc.Iterable,
            abc.Container,
            object
        )
        get_mro(Mapping) == mro
        get_mro(abc.Mapping) == mro
        get_mro(Mapping[int, str]) == mro
    """
    _, typing = get_typing(type_)
    return _get_mro(typing or type_)
