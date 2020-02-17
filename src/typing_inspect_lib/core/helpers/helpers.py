"""Common helper functions."""

import itertools
import sys
try:
    from collections.abc import MutableMapping
except ImportError:
    from collections import MutableMapping

__all__ = [
    'VERSION',
    'PY_OLD',
    'PY_35',
    'PY350_2',
    'safe_dict_get',
    'safe_dict_get_both',
    'safe_contains',
    'safe_getattr_tuple',
    'pairwise',
    'Transparent',
    'get_typings',
    'Types',
]

VERSION = sys.version_info[:3]
PY_OLD = VERSION < (3, 7, 0)
PY_35 = VERSION[:2] == (3, 5)
PY350_2 = PY_35 and VERSION <= (3, 5, 2)

_SENTINEL = object()


def safe_dict_get(dict_, key, default=None):
    """Get value from dictionary safely."""
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
    """Get value from dict and inverted dict."""
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


def safe_contains(dict_, key):
    """See if key is contained in dict, errors silently."""
    try:
        return key in dict_
    except TypeError:
        return False


def safe_getattr_tuple(type_, key):
    """Get attribute from type, defaulting to empty tuple."""
    try:
        return tuple(getattr(type_, key, None) or [])
    except TypeError:
        return ()


def pairwise(it):  # pylint: disable=invalid-name
    """
    Perform s -> (s0,s1), (s1,s2), (s2, s3), ...

    Duplicate of the :mod:`itertools` recipe.
    """
    a, b = itertools.tee(it)  # pylint: disable=invalid-name
    next(b, None)
    return zip(a, b)


class TransparentMeta(type):
    """
    Transparently pass values from another object.

    By setting the :code:`_obj` it allows you to get the values
    defined on :code:`_obj`. It also allows setting default values
    via :code:`_default`. This makes it so that if :code:`_obj` doesn't
    have that value then it will return a reasonable default value.

    If you need a attribute to be set to a certain value, then you can
    just define the value on the class. This is as only
    :meth:`TransparentMeta.__getattr__` is defined.
    """
    def __getattr__(self, item):
        if item in {'__slots__'}:
            raise AttributeError("type object '{}' has no attribute '{}'".format(self, item))

        if item in self._cache:
            return self._cache[item]

        try:
            value = getattr(self._obj, item)
        except AttributeError:
            if item in self._default:
                value = self._default[item]
            else:
                value = self._missing(item)

        # Using `_cache` breaks some objects,
        # `setattr` breaks others. (functions)
        setattr(self, item, value)
        if getattr(self, item) is not value:
            delattr(self, item)
            self._cache[item] = value
        return value


class Transparent(type.__new__(TransparentMeta, 'TransparentMeta', (), {})):
    """
    Base class for transparent objects.

    This defines :meth:`Transparent._missing` which you can overwrite if
    you want defaults to be defined in a custom way. It should be noted
    that :code:`_default` attributes are handled in
    :meth:`TransparentMeta.__getattr__`.
    """
    _default = {}
    _obj = object()
    _cache = {}

    @classmethod
    def _missing(cls, key):
        """Create default object when attribute is missing."""
        const_key = key.upper()
        if const_key != key:
            return getattr(cls, const_key)
        return type(const_key, (), {'__repr__': lambda _: const_key, '_typing': False})


if PY_OLD:
    def _is_typing(t_typing):
        return (
            getattr(t_typing, '__extra__', None) is not None
            or getattr(t_typing, '_is_protocol', False)
        )
else:
    def _is_typing(t_typing):
        return (
            getattr(t_typing, '__origin__', None) is not None
            or getattr(t_typing, '_is_protocol', False)
        )
_is_typing.__doc__ = """
Is the argument provided a typing type."""


def get_typings(typing, typing_extensions):
    """Get most typing types."""
    output = []
    for loc in (typing, typing_extensions):
        loc = loc._obj
        for attr in dir(loc):
            obj = getattr(loc, attr)
            if _is_typing(obj):
                output.append(obj)
    return output


if PY_OLD:
    def _from_typing_to_class(t_typing):
        return getattr(t_typing, '__extra__', None) or t_typing
else:
    def _from_typing_to_class(t_typing):
        return getattr(t_typing, '__origin__', None) or t_typing
_from_typing_to_class.__doc__ = """
Get :ref:`Class` type from :ref:`Unwrapped`/:ref:`Wrapped` type."""


class _Types(MutableMapping):
    """
    Mapping between two types.

    This is a two way bind, and :code:`inv` holds the inverse of this one.
    Note that :code:`self._inv[self[value]]` may not be :code:`value`.
    """

    def __init__(self):
        self._values = {}
        # Should be set to the inverse
        self._inv = {}

    def __getitem__(self, key):
        return self._values[key]

    def __setitem__(self, key, value):
        old_value = self._values.get(key, _SENTINEL)
        if old_value is not _SENTINEL:
            self._inv.pop(old_value, None)
        self._values[key] = value
        self._inv._values[value] = key

    def __delitem__(self, value):
        self._values.__delitem__(value)

    def __len__(self):
        return len(self._values)

    def __iter__(self):
        return iter(self._values)


class Types(object):  # pylint: disable=useless-object-inheritance, too-few-public-methods
    """Hold typing and class conversions."""

    def __init__(self, types):
        self.typing = _Types()
        self.class_ = _Types()
        self.typing._inv = self.class_
        self.class_._inv = self.typing

        for t_typing in types:
            self.typing[t_typing] = _from_typing_to_class(t_typing)

        self.class_to_typing = self.class_
        self.typing_to_class = self.typing
