from unittest import TestCase, skipIf

import sys
import typing
try:
    import typing_extensions
except ImportError:
    _HAS_TE = False
else:
    _HAS_TE = True
import collections
import textwrap

import typing_inspect_lib
from typing_inspect_lib._compat import abc as _abc
from .build_types import _build_tests

TKey = typing.TypeVar('TKey')
TValue = typing.TypeVar('TValue')
TSend = typing.TypeVar('TSend')
TReturn = typing.TypeVar('TReturn')

VERSION = sys.version_info[:3]
PY35 = VERSION[:2] == (3, 5)
PY36 = VERSION[:2] == (3, 6)


class BaseTestCase(TestCase):
    def _is(self, type_):
        special_type = typing_inspect_lib.get_special_type(type_)
        return (
            special_type is typing.Generic,
            special_type is typing.Tuple,
            special_type is typing.Callable,
            special_type is typing.Union,
            special_type is typing.Optional,
            special_type is typing_inspect_lib.Protocol_,
            False,
            special_type is typing_inspect_lib.Protocol_,
            special_type is typing_inspect_lib.ClassVar_,
            special_type is typing.TypeVar,
            special_type is typing_inspect_lib.NewType_
        )

    def type_test(self, type_, typing_, class_, args, is_):
        if args is not None:
            args = [typing_inspect_lib.build_types(a) for a in args]
        t = typing_inspect_lib.Type(typing_, class_, args)
        self.assertEqual(tuple(bool(int(i)) for i in '{:0>11b}'.format(is_)), self._is(type_))
        self.assertEqual(t, typing_inspect_lib.build_types(type_))

    def class_test(self, type_, typing_, class_, is_, t_args, args, before=2, after=2):
        for base, obj, special, unwrapped, args in _build_tests(type_, t_args, args, before, after):
            if not special and unwrapped and all(a in t_args for a in args):
                args = None
            else:
                args = [typing_inspect_lib.build_types(a) for a in args] or None
            if special:
                t = typing_inspect_lib.Type(typing_, class_, args)
                self.assertEqual(is_, typing_inspect_lib.get_special_type(obj))
            else:
                t = typing_inspect_lib.Type(base, base, args)
                self.assertEqual(None, typing_inspect_lib.get_special_type(obj))
            self.assertEqual(t, typing_inspect_lib.build_types(obj))


class SpecialTestCase(BaseTestCase):
    def test_any(self):
        self.assertEqual(typing_inspect_lib.build_types(typing.Any), typing_inspect_lib.LiteralType(typing.Any))

    def test_callable(self):
        _is = 0b00100000000
        self.type_test(typing.Callable, typing.Callable, _abc.Callable, None, _is)
        self.type_test(typing.Callable[[TKey], TValue], typing.Callable, _abc.Callable, [TKey, TValue], _is)

    @skipIf(PY35 and VERSION <= (3, 5, 2),
            'ClassVar not in 3.5.[0,2]')
    def test_class_var(self):
        _is = 0b00000000100
        self.type_test(typing.ClassVar, typing.ClassVar, typing.ClassVar, None, _is)
        self.type_test(typing.ClassVar[TValue], typing.ClassVar, typing.ClassVar, [TValue], _is)

    def test_generic(self):
        _is = 0b10000000000
        self.type_test(typing.Generic, typing.Generic, typing.Generic, None, _is)
        self.type_test(typing.Generic[TKey, TValue], typing.Generic, typing.Generic, [TKey, TValue], _is)

    def test_optional(self):
        _is_optional = 0b00001000000
        _is_union = 0b00010000000
        self.type_test(typing.Optional, typing.Optional, typing.Optional, None, _is_optional)
        self.type_test(typing.Optional[TValue], typing.Union, typing.Union, [TValue, type(None)], _is_union)

    def test_tuple(self):
        _is = 0b01000000000
        self.type_test(typing.Tuple, typing.Tuple, tuple, None, _is)
        self.type_test(typing.Tuple[TKey, TValue], typing.Tuple, tuple, [TKey, TValue], _is)

    @skipIf(PY35 and VERSION <= (3, 5, 1),
            'Type not in 3.5.[0,1]')
    def test_type(self):
        _is = 0b00000000000
        self.type_test(typing.Type, typing.Type, type, None, _is)
        self.type_test(typing.Type[TValue], typing.Type, type, [TValue], _is)

    def test_type_var(self):
        self.assertEqual(typing_inspect_lib.build_types(TKey), typing_inspect_lib.VarType(TKey))
        self.assertEqual(typing_inspect_lib.build_types(TValue), typing_inspect_lib.VarType(TValue))
        self.assertEqual(typing_inspect_lib.build_types(TSend), typing_inspect_lib.VarType(TSend))
        self.assertEqual(typing_inspect_lib.build_types(TReturn), typing_inspect_lib.VarType(TReturn))

    def test_union(self):
        _is = 0b010000000
        self.type_test(typing.Union, typing.Union, typing.Union, None, _is)
        self.type_test(typing.Union[TKey, TValue], typing.Union, typing.Union, [TKey, TValue], _is)


class ABCTestCase(BaseTestCase):
    def test_abstract_set(self):
        _is = 0b00000000000
        self.type_test(typing.AbstractSet, typing.AbstractSet, _abc.Set, None, _is)
        self.type_test(typing.AbstractSet[TValue], typing.AbstractSet, _abc.Set, [TValue], _is)
        self.class_test(typing.AbstractSet, typing.AbstractSet, _abc.Set, None, [TValue], [int])

    def test_byte_string(self):
        _is = 0b00000000000
        self.type_test(typing.ByteString, typing.ByteString, _abc.ByteString, None, _is)

    def test_container(self):
        _is = 0b00000000000
        self.type_test(typing.Container, typing.Container, _abc.Container, None, _is)
        self.type_test(typing.Container[TValue], typing.Container, _abc.Container, [TValue], _is)

    @skipIf(PY35 and VERSION <= (3, 5, 3),
            'ContextManager not in 3.5.[0,3]')
    def test_context_manager(self):
        _is = 0b00000000000
        self.type_test(typing.ContextManager, typing.ContextManager, _abc.AbstractContextManager, None, _is)
        self.type_test(typing.ContextManager[TValue], typing.ContextManager, _abc.AbstractContextManager, [TValue], _is)

    def test_hashable(self):
        _is = 0b00000000000
        self.type_test(typing.Hashable, typing.Hashable, _abc.Hashable, None, _is)

    def test_items_view(self):
        _is = 0b00000000000
        self.type_test(typing.ItemsView, typing.ItemsView, _abc.ItemsView, None, _is)
        if PY35 and VERSION <= (3, 5, 1):
            self.type_test(typing.ItemsView[TKey, TValue, TReturn], typing.ItemsView, _abc.ItemsView, [TKey, TValue, TReturn], _is)
        else:
            self.type_test(typing.ItemsView[TKey, TValue], typing.ItemsView, _abc.ItemsView, [TKey, TValue], _is)

    def test_iterable(self):
        _is = 0b00000000000
        self.type_test(typing.Iterable, typing.Iterable, _abc.Iterable, None, _is)
        self.type_test(typing.Iterable[TValue], typing.Iterable, _abc.Iterable, [TValue], _is)

    def test_iterator(self):
        _is = 0b00000000000
        self.type_test(typing.Iterator, typing.Iterator, _abc.Iterator, None, _is)
        self.type_test(typing.Iterator[TValue], typing.Iterator, _abc.Iterator, [TValue], _is)

    def test_keys_view(self):
        _is = 0b00000000000
        self.type_test(typing.KeysView, typing.KeysView, _abc.KeysView, None, _is)
        self.type_test(typing.KeysView[TKey], typing.KeysView, _abc.KeysView, [TKey], _is)

    def test_mapping(self):
        _is = 0b00000000000
        self.type_test(typing.Mapping, typing.Mapping, _abc.Mapping, None, _is)
        self.type_test(typing.Mapping[TKey, TValue], typing.Mapping, _abc.Mapping, [TKey, TValue], _is)

    def test_mapping_view(self):
        _is = 0b00000000000
        self.type_test(typing.MappingView, typing.MappingView, _abc.MappingView, None, _is)
        self.type_test(typing.MappingView[TKey], typing.MappingView, _abc.MappingView, [TKey], _is)

    def test_mutable_mapping(self):
        _is = 0b00000000000
        self.type_test(typing.MutableMapping, typing.MutableMapping, _abc.MutableMapping, None, _is)
        self.type_test(typing.MutableMapping[TKey, TValue], typing.MutableMapping, _abc.MutableMapping, [TKey, TValue], _is)

    def test_mutable_sequence(self):
        _is = 0b00000000000
        self.type_test(typing.MutableSequence, typing.MutableSequence, _abc.MutableSequence, None, _is)
        self.type_test(typing.MutableSequence[TValue], typing.MutableSequence, _abc.MutableSequence, [TValue], _is)

    def test_mutable_set(self):
        _is = 0b00000000000
        self.type_test(typing.MutableSet, typing.MutableSet, _abc.MutableSet, None, _is)
        self.type_test(typing.MutableSet[TValue], typing.MutableSet, _abc.MutableSet, [TValue], _is)

    def test_sequence(self):
        _is = 0b00000000000
        self.type_test(typing.Sequence, typing.Sequence, _abc.Sequence, None, _is)
        self.type_test(typing.Sequence[TValue], typing.Sequence, _abc.Sequence, [TValue], _is)

    def test_sized(self):
        _is = 0b00000000000
        self.type_test(typing.Sized, typing.Sized, _abc.Sized, None, _is)

    def test_values_view(self):
        _is = 0b00000000000
        self.type_test(typing.ValuesView, typing.ValuesView, _abc.ValuesView, None, _is)
        self.type_test(typing.ValuesView[TValue], typing.ValuesView, _abc.ValuesView, [TValue], _is)

    @skipIf(VERSION < (3, 5, 2), 'Awaitable requires Python 3.5.2')
    def test_awaitable(self):
        _is = 0b00000000000
        self.type_test(typing.Awaitable, typing.Awaitable, _abc.Awaitable, None, _is)
        self.type_test(typing.Awaitable[TValue], typing.Awaitable, _abc.Awaitable, [TValue], _is)

    @skipIf(VERSION < (3, 5, 2), 'AsyncIterator requires Python 3.5.2')
    def test_async_iterator(self):
        _is = 0b00000000000
        self.type_test(typing.AsyncIterator, typing.AsyncIterator, _abc.AsyncIterator, None, _is)
        self.type_test(typing.AsyncIterator[TValue], typing.AsyncIterator, _abc.AsyncIterator, [TValue], _is)

    @skipIf(VERSION < (3, 5, 2), 'AsyncIterable requires Python 3.5.2')
    def test_async_iterable(self):
        _is = 0b00000000000
        self.type_test(typing.AsyncIterable, typing.AsyncIterable, _abc.AsyncIterable, None, _is)
        self.type_test(typing.AsyncIterable[TValue], typing.AsyncIterable, _abc.AsyncIterable, [TValue], _is)

    @skipIf(VERSION < (3, 5, 3), 'Coroutine requires Python 3.5.3')
    def test_coroutine(self):
        _is = 0b00000000000
        self.type_test(typing.Coroutine, typing.Coroutine, _abc.Coroutine, None, _is)
        self.type_test(typing.Coroutine[TValue, TSend, TReturn], typing.Coroutine, _abc.Coroutine, [TValue, TSend, TReturn], _is)

    @skipIf(VERSION < (3, 6, 0), 'Collection requires Python 3.6')
    def test_collection(self):
        _is = 0b00000000000
        self.type_test(typing.Collection, typing.Collection, _abc.Collection, None, _is)
        self.type_test(typing.Collection[TValue], typing.Collection, _abc.Collection, [TValue], _is)

    @skipIf(
        VERSION < (3, 5, 4)
        or (PY36 and VERSION <= (3, 6, 0)),
        'AsyncGenerator requires Python 3.5.4 and not in 3.6.[0,?]')
    def test_async_generator(self):
        _is = 0b00000000000
        self.type_test(typing.AsyncGenerator, typing.AsyncGenerator, _abc.AsyncGenerator, None, _is)
        self.type_test(typing.AsyncGenerator[TValue, TSend], typing.AsyncGenerator, _abc.AsyncGenerator, [TValue, TSend], _is)

    @skipIf(
        VERSION < (3, 5, 4)
        or (PY36 and VERSION <= (3, 6, 0)),
        'AsyncContextManager requires Python 3.5.4 and not in 3.6.[0,?]')
    def test_async_context_manager(self):
        _is = 0b00000000000
        self.type_test(typing.AsyncContextManager, typing.AsyncContextManager, _abc.AbstractAsyncContextManager, None, _is)
        self.type_test(typing.AsyncContextManager[TValue], typing.AsyncContextManager, _abc.AbstractAsyncContextManager, [TValue], _is)


class ProtocolsTestCase(BaseTestCase):
    def test_reversible(self):
        _is = 0b00000000000
        self.type_test(typing.Reversible, typing.Reversible, _abc.Reversible, None, _is)
        self.type_test(typing.Reversible[TValue], typing.Reversible, _abc.Reversible, [TValue], _is)

    def test_supports_abs(self):
        _is = 0b00000000000
        self.type_test(typing.SupportsAbs, typing.SupportsAbs, typing.SupportsAbs, None, _is)

    @skipIf(VERSION < (3, 0, 0), 'SupportsBytes requires Python 3.?.?')
    def test_supports_bytes(self):
        _is = 0b00000000000
        self.type_test(typing.SupportsBytes, typing.SupportsBytes, typing.SupportsBytes, None, _is)

    def test_supports_complex(self):
        _is = 0b00000000000
        self.type_test(typing.SupportsComplex, typing.SupportsComplex, typing.SupportsComplex, None, _is)

    def test_supports_float(self):
        _is = 0b00000000000
        self.type_test(typing.SupportsFloat, typing.SupportsFloat, typing.SupportsFloat, None, _is)

    def test_supports_int(self):
        _is = 0b00000000000
        self.type_test(typing.SupportsInt, typing.SupportsInt, typing.SupportsInt, None, _is)

    @skipIf(VERSION < (3, 0, 0), 'SupportsRound requires Python 3.?.?')
    def test_supports_round(self):
        _is = 0b00000000000
        self.type_test(typing.SupportsRound, typing.SupportsRound, typing.SupportsRound, None, _is)


class CollectionTestCase(BaseTestCase):
    @skipIf((PY35 and VERSION <= (3, 5, 3)) or VERSION == (3, 6, 0),
            'Counter not in 3.5.[0,3] or 3.6.0')
    def test_counter(self):
        _is = 0b00000000000
        self.type_test(typing.Counter, typing.Counter, collections.Counter, None, _is)
        self.type_test(typing.Counter[TValue], typing.Counter, collections.Counter, [TValue], _is)

    @skipIf(VERSION < (3, 3, 0) or (PY35 and VERSION <= (3, 5, 3)) or VERSION == (3, 6, 0),
            'ChainMap requires 3.3 and not in 3.5.[0,3] or 3.6.0')
    def test_chain_map(self):
        _is = 0b00000000000
        self.type_test(typing.ChainMap, typing.ChainMap, collections.ChainMap, None, _is)
        self.type_test(typing.ChainMap[TKey, TValue], typing.ChainMap, collections.ChainMap, [TKey, TValue], _is)

    @skipIf((PY35 and VERSION <= (3, 5, 3)) or VERSION == (3, 6, 0),
            'Deque not in 3.5.[0,3] or 3.6.0')
    def test_deque(self):
        _is = 0b00000000000
        self.type_test(typing.Deque, typing.Deque, collections.deque, None, _is)
        self.type_test(typing.Deque[TValue], typing.Deque, collections.deque, [TValue], _is)

    def test_dict(self):
        dict_ = _abc.MutableMapping if PY35 and (VERSION <= (3, 5, 1)) else dict

        _is = 0b00000000000
        self.type_test(typing.Dict, typing.Dict, dict_, None, _is)
        self.type_test(typing.Dict[TKey, TValue], typing.Dict, dict_, [TKey, TValue], _is)

    @skipIf((PY35 and VERSION <= (3, 5, 1)),
            'DefaultDict not in 3.5.[0,1]')
    def test_default_dict(self):
        _is = 0b00000000000
        self.type_test(typing.DefaultDict, typing.DefaultDict, collections.defaultdict, None, _is)
        self.type_test(typing.DefaultDict[TKey, TValue], typing.DefaultDict, collections.defaultdict, [TKey, TValue], _is)

    def test_list(self):
        list_ = _abc.MutableSequence if PY35 and (VERSION <= (3, 5, 1)) else list

        _is = 0b00000000000
        self.type_test(typing.List, typing.List, list_, None, _is)
        self.type_test(typing.List[TValue], typing.List, list_, [TValue], _is)

    def test_set(self):
        set_ = _abc.MutableSet if PY35 and (VERSION <= (3, 5, 1)) else set

        _is = 0b00000000000
        self.type_test(typing.Set, typing.Set, set_, None, _is)
        self.type_test(typing.Set[TValue], typing.Set, set_, [TValue], _is)

    def test_frozen_set(self):
        frozenset_ = _abc.Set if PY35 and (VERSION <= (3, 5, 1)) else frozenset

        _is = 0b00000000000
        self.type_test(typing.FrozenSet, typing.FrozenSet, frozenset_, None, _is)
        self.type_test(typing.FrozenSet[TValue], typing.FrozenSet, frozenset_, [TValue], _is)

    def test_named_tuple(self):
        _is = 0b00000000000
        TestTuple = typing.NamedTuple('TestTuple', [('key', TKey), ('value', TValue)])

        self.type_test(typing.NamedTuple, typing.NamedTuple, typing.NamedTuple, None, _is)
        self.type_test(TestTuple, None, None, None, _is)

    @skipIf(VERSION < (3, 7, 2), 'OrderedDict requires Python 3.7.2')
    def test_ordered_dict(self):
        _is = 0b00000000000
        self.type_test(typing.OrderedDict, typing.OrderedDict, collections.OrderedDict, None, _is)
        self.type_test(typing.OrderedDict[TKey, TValue], typing.OrderedDict, collections.OrderedDict, [TKey, TValue], _is)

    def test_generator(self):
        _is = 0b00000000000
        self.type_test(typing.Generator, typing.Generator, _abc.Generator, None, _is)
        self.type_test(typing.Generator[TValue, TSend, TReturn], typing.Generator, _abc.Generator, [TValue, TSend, TReturn], _is)


class OneOffTestCase(BaseTestCase):
    def test_anystr(self):
        self.assertEqual(typing_inspect_lib.build_types(typing.AnyStr), typing_inspect_lib.VarType(typing.AnyStr))

    @skipIf(PY35 and VERSION <= (3, 5, 1),
            'NewType not in 3.5.[0,1]')
    def test_new_type(self):
        TestType = typing.NewType('TestType', int)
        self.assertEqual(typing_inspect_lib.build_types(TestType), typing_inspect_lib.NewType(TestType))

    @skipIf((PY35 and VERSION <= (3, 5, 3))
            or (PY36 and VERSION <= (3, 6, 0)),
            'NoReturn not in 3.5.[0,3] or 3.6.[0,?]')
    def test_no_return(self):
        self.assertEqual(typing_inspect_lib.build_types(typing.NoReturn), typing_inspect_lib.LiteralType(typing.NoReturn))

    @skipIf(PY35 and VERSION <= (3, 5, 1),
            'Text not in 3.5.[0,1]')
    def test_text(self):
        self.assertEqual(typing_inspect_lib.build_types(typing.Text), typing_inspect_lib.LiteralType(typing.Text))


@skipIf(not _HAS_TE, 'Typing extension test require it to be installed.')
class ExtensionsTestCase(BaseTestCase):
    @skipIf(VERSION < (3, 3, 0) or VERSION == (3, 5, 0),
            'te.Protocol requires Python 3 and not in 3.5.0')
    def test_protocol(self):
        _is = 0b000101000
        proto = textwrap.dedent('''
        class TestProtocol(typing_extensions.Protocol):
            def fn(self, a: int) -> int:
                ...
        ''')

        globals_ = {'typing_extensions': typing_extensions}
        exec(proto, globals_)
        TestProtocol = globals_['TestProtocol']
        self.type_test(typing_extensions.Protocol, typing_extensions.Protocol, typing_extensions.Protocol, None, _is)
        self.type_test(TestProtocol, typing_extensions.Protocol, TestProtocol, None, _is)

    # Special
    def test_class_var(self):
        _is = 0b000000100
        self.type_test(typing_extensions.ClassVar, typing_inspect_lib.ClassVar_, typing_inspect_lib.ClassVar_, None, _is)
        self.type_test(typing_extensions.ClassVar[TValue], typing_inspect_lib.ClassVar_, typing_inspect_lib.ClassVar_, [TValue], _is)

    def test_type(self):
        _is = 0b00000000000
        self.type_test(typing_extensions.Type, typing_extensions.Type, type, None, _is)
        self.type_test(typing_extensions.Type[TValue], typing_extensions.Type, type, [TValue], _is)

    # ABCs
    def test_context_manager(self):
        _is = 0b00000000000
        self.type_test(typing_extensions.ContextManager, typing_extensions.ContextManager, _abc.AbstractContextManager, None, _is)
        self.type_test(typing_extensions.ContextManager[TValue], typing_extensions.ContextManager, _abc.AbstractContextManager, [TValue], _is)

    @skipIf(VERSION < (3, 5, 0), 'te.Awaitable requires Python 3.5')
    def test_awaitable(self):
        _is = 0b00000000000
        self.type_test(typing_extensions.Awaitable, typing_extensions.Awaitable, _abc.Awaitable, None, _is)
        self.type_test(typing_extensions.Awaitable[TValue], typing_extensions.Awaitable, _abc.Awaitable, [TValue], _is)

    @skipIf(VERSION < (3, 5, 0), 'te.AsyncIterator requires Python 3.5')
    def test_async_iterator(self):
        _is = 0b00000000000
        self.type_test(typing_extensions.AsyncIterator, typing_extensions.AsyncIterator, _abc.AsyncIterator, None, _is)
        self.type_test(typing_extensions.AsyncIterator[TValue], typing_extensions.AsyncIterator, _abc.AsyncIterator, [TValue], _is)

    @skipIf(VERSION < (3, 5, 0), 'te.AsyncIterable requires Python 3.5')
    def test_async_iterable(self):
        _is = 0b00000000000
        self.type_test(typing_extensions.AsyncIterable, typing_extensions.AsyncIterable, _abc.AsyncIterable, None, _is)
        self.type_test(typing_extensions.AsyncIterable[TValue], typing_extensions.AsyncIterable, _abc.AsyncIterable, [TValue], _is)

    @skipIf(VERSION < (3, 5, 0), 'te.Coroutine requires Python 3.5')
    def test_coroutine(self):
        _is = 0b00000000000
        self.type_test(typing_extensions.Coroutine, typing_extensions.Coroutine, _abc.Coroutine, None, _is)
        self.type_test(typing_extensions.Coroutine[TValue, TSend, TReturn], typing_extensions.Coroutine, _abc.Coroutine, [TValue, TSend, TReturn], _is)

    @skipIf(VERSION < (3, 6, 0), 'te.AsyncGenerator requires Python 3.6')
    def test_async_generator(self):
        _is = 0b00000000000
        self.type_test(typing_extensions.AsyncGenerator, typing_extensions.AsyncGenerator, _abc.AsyncGenerator, None, _is)
        self.type_test(typing_extensions.AsyncGenerator[TValue, TSend], typing_extensions.AsyncGenerator, _abc.AsyncGenerator, [TValue, TSend], _is)

    @skipIf(VERSION < (3, 5, 0), 'te.AsyncContextManager requires Python 3.5')
    def test_async_context_manager(self):
        _is = 0b00000000000
        self.type_test(typing_extensions.AsyncContextManager, typing_extensions.AsyncContextManager, _abc.AbstractAsyncContextManager, None, _is)
        self.type_test(typing_extensions.AsyncContextManager[TValue], typing_extensions.AsyncContextManager, _abc.AbstractAsyncContextManager, [TValue], _is)

    @skipIf(VERSION < (3, 3, 0), 'te.ChainMap requires Python 3.3')
    def test_chain_map(self):
        _is = 0b00000000000
        self.type_test(typing_extensions.ChainMap, typing_extensions.ChainMap, collections.ChainMap, None, _is)
        self.type_test(typing_extensions.ChainMap[TKey, TValue], typing_extensions.ChainMap, collections.ChainMap, [TKey, TValue], _is)

    # collection
    def test_counter(self):
        _is = 0b00000000000
        self.type_test(typing_extensions.Counter, typing_extensions.Counter, collections.Counter, None, _is)
        if PY35 and VERSION <= (3, 5, 1):
            self.type_test(typing_extensions.Counter[TValue], typing_extensions.Counter, collections.Counter, [TValue, int], _is)
        else:
            self.type_test(typing_extensions.Counter[TValue], typing_extensions.Counter, collections.Counter, [TValue], _is)

    def test_deque(self):
        _is = 0b00000000000
        self.type_test(typing_extensions.Deque, typing_extensions.Deque, collections.deque, None, _is)
        self.type_test(typing_extensions.Deque[TValue], typing_extensions.Deque, collections.deque, [TValue], _is)

    def test_default_dict(self):
        _is = 0b00000000000
        self.type_test(typing_extensions.DefaultDict, typing_extensions.DefaultDict, collections.defaultdict, None, _is)
        self.type_test(typing_extensions.DefaultDict[TKey, TValue], typing_extensions.DefaultDict, collections.defaultdict, [TKey, TValue], _is)

    # One-off
    def test_new_type(self):
        TestType = typing_extensions.NewType('TestType', int)
        self.assertEqual(typing_inspect_lib.build_types(TestType), typing_inspect_lib.NewType(TestType))

    def test_no_return(self):
        self.assertEqual(typing_inspect_lib.build_types(typing_extensions.NoReturn), typing_inspect_lib.LiteralType(typing_extensions.NoReturn))

    def test_text(self):
        self.assertEqual(typing_inspect_lib.build_types(typing_extensions.Text), typing_inspect_lib.LiteralType(typing_extensions.Text))
