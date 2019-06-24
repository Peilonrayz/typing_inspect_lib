"""
Typing inspect library for common inspection functions.

Allows type inspections for the :py:mod:`typing`
and `Typing Extensions`_ libraries.
Works in Python 2.7 and 3 - Python 3.5.0+ is supported.

.. _Typing Extensions: https://github.com/python/typing/tree/master/typing_extensions

This library is designed to ease use in all Python versions,
and so functions like :py:func:`typing_inspect_lib.get_typing`
return multiple types.
The rational for this comes in three parts:

1.  Different versions of Python change what types they hold.
    Take :code:`__origin__`, which changed from returning typing types
    (e.g. :py:class:`typing.Mapping`) to class types
    (e.g. :py:class:`collections.abc.Mapping`) in Python 3.7.

    Meaning the function :code:`get_origin` would have version
    incompatibilities between 3.7 and other versions of Python.

2.  Different versions of Python contain different information.
    Take :code:`__extra__`, which was removed in Python 3.7.

    Meaning there isn't an easy way to get the typing type from
    a :code:`get_origin` function in Python 3.7.
    And the result from a :code:`get_extra` function is always :code:`None`.

3.  Internally converting to and from typing and class types is easy.
    Meaning there's little overhead to returning all the available types.

And so your code can focus on using the type information you need,
rather than having to check version incompatibilities.
Whilst the library is designed to reduce version incompatibility it doesn't
guarantee that there are none.
Please look at :ref:`python-compatibility` to see which are known.
"""

from .core import get_args, get_parameters, get_type_info, get_typing
from .core.helpers import (
    typing as _typing,
    typing_extensions as _typing_extensions,
)
from .extras import get_bases, get_mro, get_mro_orig, get_type_var_info

__all__ = [
    'get_args',
    'get_bases',
    'get_type_info',
    # 'get_generic_type',
    'get_parameters',
    'get_type_var_info',
    'get_typing',
    'get_mro',
    'get_mro_orig',

    # Types returned by `get_typing` for compatibility
    'ClassVar_',
    'NewType_',

    # Types returned by `get_generic_type` for compatibility
    'Protocol_',
    'BaseProtocol_',
]

NewType_ = _typing_extensions.NewType
Protocol_ = _typing_extensions.Protocol

ClassVar_ = _typing._ClassVar
BaseProtocol_ = _typing.Protocol
