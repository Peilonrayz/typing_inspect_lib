import contextlib
import collections
import sys
import types
import typing

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
    'AbstractAsyncContextManager'
]

if _VERSION < (3, 3, 0):
    _collections = collections
else:
    _collections = collections.abc

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
AbstractContextManager = getattr(contextlib, 'AbstractContextManager', getattr(typing, 'ContextManager', None))
AbstractAsyncContextManager = getattr(contextlib, 'AbstractAsyncContextManager', getattr(typing, 'AsyncContextManager', None))
