import itertools


_SENTINEL = object()


def _safe_dict_get(dict_, key, default=None):
    try:
        value = dict_.get(key, _SENTINEL)
    except TypeError:
        return default
    else:
        if value is _SENTINEL:
            return default
        return value


def _safe_dict_contains(dict_, key):
    try:
        return key in dict_
    except TypeError:
        return False


def _safe_getattr_tuple(type_, key):
    try:
        return tuple(getattr(type_, key, None) or [])
    except TypeError:
        return ()


def _pairwise(it):
    a, b = itertools.tee(it)
    next(b, None)
    return zip(a, b)