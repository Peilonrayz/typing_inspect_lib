import typing

from .get_base_type import get_base_type
from .get_origins import _get_origins
from .get_typing import get_typing
from .helpers import (
    PY_35, PY_OLD, VERSION, is_special, safe_getattr_tuple, typing_,
)

# TODO: reduce complexity
if PY_35 and VERSION <= (3, 5, 2):  # noqa: MC0001
    # pylint: disable=too-many-return-statements
    def _handle_special_type(type_, t_typing):
        """Get args for types that can't be handled via normal means."""
        if is_special(t_typing):
            if t_typing is typing_.ClassVar:
                return (type_.__type__,) if type_.__type__ is not None else ()
            if t_typing is typing.Callable:
                args = type_.__args__
                ret = type_.__result__
                if args is None and ret is None:
                    return ()
                return tuple(args) + (ret,)
            if t_typing is typing.Generic:
                return type_.__parameters__ or ()
            if t_typing is typing.Union:
                return type_.__union_params__ or ()
            if t_typing is typing.Tuple:
                return type_.__tuple_params__ or ()
        return None
elif PY_OLD:
    def _handle_special_type(type_, t_typing):
        if t_typing is typing.ClassVar:
            return (type_.__type__,) if type_.__type__ is not None else ()
        return None


def _parameters_link(args, parameters):
    """Build arguments based on the arguments and parameters provided."""
    args_ = {}
    for index, arg in enumerate(args):
        args_.setdefault(arg, []).append(index)
    args_ = {key: iter(value) for key, value in args_.items()}
    return [next(args_.get(p, iter([p]))) for p in parameters]


if PY_35 and VERSION <= (3, 5, 1):
    def _handle_origin(type_):
        """Get arguments of provided type based on the origins of the type."""
        if getattr(type_, '__origin__', None) is not None:
            return safe_getattr_tuple(type_, '__parameters__')
        return None
elif PY_OLD:
    def _handle_origin(type_):
        origins = _get_origins(type_)
        origin, origins = origins[0], origins[1:]
        args = list(safe_getattr_tuple(origin, '__args__'))
        for origin_ in origins:
            links = _parameters_link(args, safe_getattr_tuple(origin, '__parameters__'))
            origin = origin_
            for link, arg in zip(links, safe_getattr_tuple(origin, '__args__')):
                args[link] = arg
        return tuple(args)


SENTINEL = object()


if PY_OLD:
    def _get_args(type_, t_typing=SENTINEL):
        if type(type_) is typing._TypeAlias:  # pylint: disable=unidiomatic-typecheck
            return (type_.type_var,)
        _, base = get_base_type(type_)
        if base:
            return ()
        if t_typing is SENTINEL:
            t_typing, _ = get_typing(type_)
        special_args = _handle_special_type(type_, t_typing)
        if special_args is not None:
            return special_args
        origin_args = _handle_origin(type_)
        if origin_args is not None:
            return origin_args
        return ()
else:
    def _get_args(type_, t_typing=SENTINEL):  # pylint: disable=unused-argument
        _, base = get_base_type(type_)
        if base:
            return ()
        return getattr(type_, '__args__', None) or ()


def get_args(type_):
    """Get the arguments stored in the type provided.

    Examples:

        get_args(Mapping) == ()
        get_args(Mapping[str, int]) == (str, int)
        get_args(Mapping[Union[str, int], int]) == (Union, Union)
    """
    return _get_args(type_)
