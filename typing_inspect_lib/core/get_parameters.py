import typing

from .helpers import PY_35, VERSION, PY_OLD, safe_getattr_tuple, typing_

from .get_typing import get_typing
from .get_args import get_args

SENTINEL = object()

if PY_35 and VERSION <= (3, 5, 2):
    _USE_ARGS = {
        typing_.ClassVar,
        typing.Callable,
        typing.Union,
        typing.Tuple
    }

    def _get_parameters(type_, t_typing=SENTINEL):
        if t_typing is SENTINEL:
            t_typing, _ = get_typing(type_)
        if t_typing in _USE_ARGS:
            parameters = get_args(type_)
        else:
            parameters = getattr(type_, '__parameters__', None) or ()
        return tuple(p for p in parameters if isinstance(p, typing.TypeVar))
elif PY_OLD:
    def _get_parameters(type_, t_typing=SENTINEL):
        if t_typing is SENTINEL:
            t_typing, _ = get_typing(type_)
        if t_typing is typing_.ClassVar:
            return get_args(type_)
        return safe_getattr_tuple(type_, '__parameters__')
else:
    def _get_parameters(type_, t_typing=SENTINEL):
        return safe_getattr_tuple(type_, '__parameters__')


def get_parameters(type_):
    """
    Gets the parameters of the type provided.

    Examples:

        get_parameters(Mapping[str, int]) == ()
        get_parameters(Mapping[TKey, TValue]) == (TKey, TValue)
    """
    return _get_parameters(type_)
