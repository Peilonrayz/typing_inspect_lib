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

from .helpers import Transparent


class typing_extensions(Transparent):
    """Interface to Typing Extensions."""
    _obj = _typing_extensions


class typing(Transparent):
    """
    Interface to :mod:`typing`.

    Ensures the following are defined:

    - :class:`typing._Union`.
    - :class:`typing._ClassVar`.
    """
    _obj = _typing
    _default = {
        '_Union': _typing.Union,
        '_ClassVar': getattr(_typing, 'ClassVar', typing_extensions.ClassVar)
    }


typings = typing_extensions if HAS_TE else typing


class abc(Transparent):
    """
    Interface to :mod:`collections.abc`.

    Ensures the following are defined:

    - :class:`collections.abc.Generator`.
    - :class:`collections.abc.ByteString`.
    - :class:`collections.abc.Reversible`.
    """
    _obj = _abc
    _default = {
        'Generator': _types.GeneratorType,
        'ByteString': typing.ByteString,
        'Reversible': typing.Reversible,
    }


class contextlib(Transparent):
    """
    Interface to :mod:`contextlib`.

    Ensures the following are defined:

    - :class:`contextlib.AbstractContextManager`.
    - :class:`contextlib.AbstractAsyncContextManager`.
    """
    _obj = _contextlib
    _default = {
        'AbstractContextManager': typings.ContextManager,
        'AbstractAsyncContextManager': typings.AsyncContextManager,
    }


class re(Transparent):
    """
    Interface to :mod:`re`.

    Ensures the following are defined:

    - :class:`re.Pattern`.
    - :class:`re.Match`.
    """
    _obj = _re
    _default = {
        'Pattern': type(_sre_compile.compile('', 0)),
        'Match': type(_sre_compile.compile('', 0).match('')),
    }
