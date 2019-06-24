try:
    import collections.abc as _abc
except ImportError:
    import collections as _abc
import contextlib as _contextlib
import typing as _typing
import types as _types
import re as _re
import sre_compile as _sre_compile
try:
    import typing_extensions as _typing_extensions
except ImportError:
    _typing_extensions = object()
    HAS_TE = False
else:
    HAS_TE = True


class TransparentMeta(type):
    def __getattr__(self, item):
        if item in self._cache:
            return self._cache[item]

        try:
            value = getattr(self._obj, item)
        except AttributeError:
            if item in self._default:
                value = self._default[item]
            else:
                value = self._missing(item)

        setattr(self, item, value)
        if getattr(self, item) is not value:
            delattr(self, item)
            self._cache[item] = value
        return value


class Transparent(type.__new__(TransparentMeta, 'TransparentMeta', (), {})):
    _default = {}
    _obj = object()
    _cache = {}

    @classmethod
    def _missing(cls, key):
        const_key = key.upper()
        if const_key != key:
            return getattr(cls, const_key)
        return type(const_key, (), {'__repr__': lambda _: const_key})


class typing_extensions(Transparent):
    _obj = _typing_extensions


class typing(Transparent):
    _obj = _typing
    _default = {
        '_Union': _typing.Union,
        '_ClassVar': getattr(_typing, 'ClassVar', typing_extensions.ClassVar)
    }


typings = typing_extensions if HAS_TE else typing


class abc(Transparent):
    _obj = _abc
    _default = {
        'Generator': _types.GeneratorType,
        'ByteString': typing.ByteString,
        'Reversible': typing.Reversible,
    }


class contextlib(Transparent):
    _obj = _contextlib
    _default = {
        'AbstractContextManager': typings.ContextManager,
        'AbstractAsyncContextManager': typings.AsyncContextManager,
    }


class re(Transparent):
    _obj = _re
    _default = {
        'Pattern': type(_sre_compile.compile('', 0)),
        'Match': type(_sre_compile.compile('', 0).match('')),
    }
