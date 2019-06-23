# pylint: disable=invalid-name
"""Interface to :mod:`collections.abc`."""

try:
    import collections.abc as _collections
except ImportError:
    import collections as _collections
import contextlib
import sys
import types
import typing
try:
    import typing_extensions
except ImportError:
    _HAS_TE = False
else:
    _HAS_TE = True

_VERSION = sys.version_info[:3]

__all__ = [
    # collections.abc
    'Container',
    'Hashable',
    'Iterable',
    'Iterator',
    'Sized',
    'Callable',
    'Mapping',
    'MutableMapping',
    'Sequence',
    'MutableSequence',
    'Set',
    'MutableSet',
    'MappingView',
    'ItemsView',
    'KeysView',
    'ValuesView',
    'Generator',
    'ByteString',
    'Awaitable',
    'Coroutine',
    'AsyncIterable',
    'AsyncIterator',
    'Collection',
    'Reversible',
    'AsyncGenerator',

    # contextlib
    'AbstractContextManager',
    'AbstractAsyncContextManager',
]

Container = _collections.Container
Hashable = _collections.Hashable
Iterable = _collections.Iterable
Iterator = _collections.Iterator
Sized = _collections.Sized
Callable = _collections.Callable
Mapping = _collections.Mapping
MutableMapping = _collections.MutableMapping
Sequence = _collections.Sequence
MutableSequence = _collections.MutableSequence
Set = _collections.Set
MutableSet = _collections.MutableSet
MappingView = _collections.MappingView
ItemsView = _collections.ItemsView
KeysView = _collections.KeysView
ValuesView = _collections.ValuesView

# New in 3.5
Generator = getattr(_collections, 'Generator', types.GeneratorType)
ByteString = getattr(_collections, 'ByteString', typing.ByteString)
Awaitable = getattr(_collections, 'Awaitable', None)
Coroutine = getattr(_collections, 'Coroutine', None)
AsyncIterable = getattr(_collections, 'AsyncIterable', None)
AsyncIterator = getattr(_collections, 'AsyncIterator', None)

# New in 3.6
Collection = getattr(_collections, 'Collection', None)
Reversible = getattr(_collections, 'Reversible', typing.Reversible)
AsyncGenerator = getattr(_collections, 'AsyncGenerator', None)

# contextlib ABC
if _HAS_TE:
    _ContextManager = getattr(typing_extensions, 'ContextManager', None)
    _AsyncContextManager = getattr(typing_extensions, 'AsyncContextManager', None)
else:
    _ContextManager = getattr(typing, 'ContextManager', None)
    _AsyncContextManager = getattr(typing, 'AsyncContextManager', None)

AbstractContextManager = getattr(contextlib, 'AbstractContextManager', _ContextManager)
AbstractAsyncContextManager = getattr(contextlib, 'AbstractAsyncContextManager',
                                      _AsyncContextManager)
