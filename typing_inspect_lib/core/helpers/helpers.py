import sys
import itertools

__all__ = [
    'VERSION',
    'PY_OLD',
    'PY_35',
    'PY350_2',
    'safe_dict_get',
    'safe_dict_contains',
    'safe_getattr_tuple',
    'pairwise'
]

VERSION = sys.version_info[:3]
PY_OLD = VERSION < (3, 7, 0)
PY_35 = VERSION[:2] == (3, 5)
PY350_2 = PY_35 and VERSION <= (3, 5, 2)

_SENTINEL = object()


def safe_dict_get(dict_, key, default=None):
    try:
        value = dict_.get(key, _SENTINEL)
    except TypeError:
        return default
    else:
        if value is _SENTINEL:
            return default
        return value


def safe_dict_contains(dict_, key):
    try:
        return key in dict_
    except TypeError:
        return False


def safe_getattr_tuple(type_, key):
    try:
        return tuple(getattr(type_, key, None) or [])
    except TypeError:
        return ()


def pairwise(it):
    a, b = itertools.tee(it)
    next(b, None)
    return zip(a, b)
