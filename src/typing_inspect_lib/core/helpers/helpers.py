import itertools
import sys

__all__ = [
    'VERSION',
    'PY_OLD',
    'PY_35',
    'PY350_2',
    'safe_dict_get',
    'safe_dict_get_both',
    'safe_dict_contains',
    'safe_getattr_tuple',
    'pairwise',
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


# pylint: disable=too-many-branches
def safe_dict_get_both(dict_, key, default=None, inv=False):
    try:
        value = dict_.get(key, _SENTINEL)
    except TypeError:
        return default
    else:
        if value is _SENTINEL:
            return default
    try:
        key = dict_._inv.get(value, _SENTINEL)
    except TypeError:
        return default
    else:
        if key is _SENTINEL:
            return default
        value = (key, value)
        if inv:
            value = reversed(value)
        return tuple(value)


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


def pairwise(it):  # pylint: disable=invalid-name
    a, b = itertools.tee(it)  # pylint: disable=invalid-name
    next(b, None)
    return zip(a, b)
