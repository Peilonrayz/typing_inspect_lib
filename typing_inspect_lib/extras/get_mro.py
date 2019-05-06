from ..core.helpers import PY_35, PY_OLD, VERSION, TYPING_OBJECTS, safe_dict_contains, safe_dict_get, safe_getattr_tuple

from ..core import get_typing


def _get_mro_conv_dedupe(mro):
    collection_mro = iter(
        safe_dict_get(TYPING_OBJECTS.typing_to_class, obj) or obj
        for obj in reversed(mro)
    )
    mro = ()
    mro_set = set()
    for obj in collection_mro:
        if obj not in mro_set:
            mro_set.add(obj)
            mro += obj,
    return tuple(reversed(mro))


def _from_types(types, index=1):
    mro = ()
    for type_ in types:
        t = get_typing(type_)[index]
        mro += type_ if t is None else t,
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

    Builtin types are converted to their class type to get the MRO and so `Generic` is missing.

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
    type_ = safe_dict_get(TYPING_OBJECTS.typing_to_class, type_) or type_
    if not safe_dict_contains(TYPING_OBJECTS.class_types, type_):
        _, type_ = get_typing(type_)
    return _get_mro(type_)
