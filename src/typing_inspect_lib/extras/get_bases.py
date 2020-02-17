"""Get bases."""

import collections

from ..core import get_parameters, get_type_info, get_typing
from ..core.get_type_info import _TypeInfo
from ..core.helpers import helpers, links

_BaseObj = collections.namedtuple('BaseObj', ['unwrapped', 'origin', 'orig'])


def _get_bases_typing(type_):
    """Get the bases of type, where the types bases are typing types."""
    bases = helpers.safe_getattr_tuple(type_, '__bases__')
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
    """Get the bases of type, where the types bases are class types."""
    bases = helpers.safe_getattr_tuple(type_, '__bases__')
    if not bases:
        return None
    return tuple(
        (
            get_typing(t_class)[0] or t_class,
            t_class,
        )
        for t_class in bases
    )


if helpers.PY_35 and helpers.VERSION <= (3, 5, 2):
    def _get_bases_default(type_):
        bases = _bases(type_)
        if bases is None:
            return None
        return tuple((i.unwrapped, i.origin) for i in bases)
elif helpers.PY_OLD:
    def _get_bases_default(type_):
        if links.is_typing(type_):
            return _get_bases_class(type_)
        else:
            return _get_bases_typing(type_)
else:
    def _get_bases_default(type_):
        """Get the bases of type. Returns both typing type and class type."""
        return _get_bases_class(type_)


# TODO: reduce complexity
if helpers.PY_35 and helpers.VERSION <= (3, 5, 2):  # noqa: MC0001
    def _bases(type_):
        u_type, _ = get_typing(type_)
        type_ = u_type or type_
        origins = helpers.safe_getattr_tuple(type_, '__bases__')
        if not origins:
            return ()
        mro = ()
        for orig in origins:
            type_info = get_type_info(orig)
            if type_info is None:
                if orig is object:
                    type_info = _TypeInfo(orig, orig, None, (), ())
                else:
                    raise ValueError('invalid origin type {0} {1}'.format(type_, orig))
            mro += (_BaseObj(
                type_info.unwrapped,
                type_info.origin,
                orig if len(type_info.args) > len(type_info.parameters) else None,
            ),)
        return mro
else:
    def _bases(type_):
        """Get bases from the type."""
        base_defaults = _get_bases_default(type_)
        if base_defaults is None:
            return ()

        orig_bases = {}
        for base in helpers.safe_getattr_tuple(type_, '__orig_bases__'):
            _, o_type = get_typing(base)
            orig_bases.setdefault(o_type, []).append(base)

        orig_bases = {k: iter(v) for k, v in orig_bases.items()}

        sentinel = object()
        bases = ()
        for u_type, o_type in base_defaults:
            if o_type not in orig_bases:
                bases += (_BaseObj(u_type, o_type, None),)
                continue
            base = next(orig_bases[o_type], sentinel)
            if base is sentinel:
                del orig_bases[o_type]
                bases += (_BaseObj(u_type, o_type, None),)
            else:
                bases += (_BaseObj(u_type, o_type, base),)

        left_over = [i for lst in orig_bases.values() for i in lst]
        if left_over:
            raise ValueError(
                'Did not consume all orig_bases for the class provided. {0}'
                .format(left_over),
            )
        return bases


def get_bases(type_):
    """
    Get the bases of the type, return the typing type, class type and orig type.

    Examples (Python 3.7):

    .. doctest::

        >>> get_bases(Mapping)
        (BaseObj(typing=typing.Collection, class_=<class 'collections.abc.Collection'>, orig=None),)
        >>> get_bases(abc.Mapping)
        (BaseObj(typing=typing.Collection, class_=<class 'collections.abc.Collection'>, orig=None),)
        >>> get_bases(Mapping[int, int])
        (BaseObj(typing=typing.Collection, class_=<class 'collections.abc.Collection'>, orig=typing.Collection[int]),)
    """
    type_info = get_type_info(type_)
    if type_info is None:
        return _bases(type_)
    if (
        not type_info.args
        or not links.is_typing(type_info.origin)
    ):
        return _bases(type_info.origin)
    bases = ()
    for base in _bases(type_info.origin):
        if not links.is_typing(base.origin):
            bases += (base,)
        else:
            parameters = get_parameters(base.unwrapped)
            if parameters:
                bases += (_BaseObj(
                    base.unwrapped,
                    base.origin,
                    base.unwrapped[type_info.args[:len(parameters)]],
                ),)
            else:
                bases += (base,)
    return bases
