import collections

from ..core import get_parameters, get_type_info, get_typing
from ..core.get_type_info import _TypeInfo
from ..core.helpers import (
    PY_35, PY_OLD, VERSION, is_typing, safe_getattr_tuple,
)

_BaseObj = collections.namedtuple('BaseObj', ['typing', 'class_', 'orig'])


def _get_bases_typing(type_):
    """Get the bases of type, where the types bases are typing types"""
    bases = safe_getattr_tuple(type_, '__bases__')
    if not bases:
        return None
    return tuple(
        (
            t_type,
            get_typing(t_type)[1] or t_type,
        )
        for t_type in bases
    )


def _get_bases_class(type_):
    """Get the bases of type, where the types bases are class types"""
    bases = safe_getattr_tuple(type_, '__bases__')
    if not bases:
        return None
    return tuple(
        (
            get_typing(t_class)[0] or t_class,
            t_class,
        )
        for t_class in bases
    )


if PY_35 and VERSION <= (3, 5, 2):
    def _get_bases_default(type_):
        """Get the bases of type. Returns both typing type and class type."""
        bases = _bases(type_)
        if bases is None:
            return None
        return tuple((i.typing, i.class_) for i in bases)
elif PY_OLD:
    def _get_bases_default(type_):
        if is_typing(type_):
            return _get_bases_class(type_)
        else:
            return _get_bases_typing(type_)
else:
    def _get_bases_default(type_):
        return _get_bases_class(type_)


# TODO: reduce complexity
if PY_35 and VERSION <= (3, 5, 2):  # noqa: MC0001
    def _bases(type_):
        t_typing, _ = get_typing(type_)
        type_ = t_typing or type_
        origins = safe_getattr_tuple(type_, '__bases__')
        if not origins:
            return ()
        mro = ()
        for orig in origins:
            type_info = get_type_info(orig)
            if type_info is None:
                if orig is object:
                    type_info = _TypeInfo(orig, orig, (), ())
                else:
                    raise ValueError('invalid origin type {0} {1}'.format(type_, orig))
            mro += (_BaseObj(
                type_info.typing,
                type_info.class_,
                orig if len(type_info.args) > len(type_info.parameters) else None,
            ),)
        return mro
else:
    def _bases(type_):
        base_defaults = _get_bases_default(type_)
        if base_defaults is None:
            return ()

        orig_bases = {}
        for base in safe_getattr_tuple(type_, '__orig_bases__'):
            _, class_ = get_typing(base)
            orig_bases.setdefault(class_, []).append(base)

        orig_bases = {k: iter(v) for k, v in orig_bases.items()}

        sentinel = object()
        bases = ()
        for typing_, class_ in base_defaults:
            if class_ not in orig_bases:
                bases += (_BaseObj(typing_, class_, None),)
                continue
            base = next(orig_bases[class_], sentinel)
            if base is sentinel:
                del orig_bases[class_]
                bases += (_BaseObj(typing_, class_, None),)
            else:
                bases += (_BaseObj(typing_, class_, base),)

        left_over = [i for lst in orig_bases.values() for i in lst]
        if left_over:
            raise ValueError(
                'Did not consume all orig_bases for the class provided. {0}'
                .format(left_over),
            )
        return bases


def get_bases(type_):
    """
    Gets the bases of the type, returns the typing type, class type and orig type.

    Examples (Python 3.7):

        get_bases(Mapping) == ((typing.Collection, abc.Collection, None),)
        get_bases(abc.Mapping) == ((typing.Collection, abc.Collection, None),)
        get_bases(Mapping[int, int]) == (
            (typing.Collection, abc.Collection, typing.Collection[int]),
        )
    """
    type_info = get_type_info(type_)
    if type_info is None:
        return _bases(type_)
    if (
        not type_info.args
        or not is_typing(type_info.class_)
    ):
        return _bases(type_info.class_)
    bases = ()
    for base in _bases(type_info.class_):
        if not is_typing(base.class_):
            bases += (base,)
        else:
            parameters = get_parameters(base.typing)
            if parameters:
                bases += (_BaseObj(
                    base.typing,
                    base.class_,
                    base.typing[type_info.args[:len(parameters)]],
                ),)
            else:
                bases += (base,)
    return bases
