import collections
import sys
import textwrap
import typing
from operator import eq, ge
from unittest import TestCase, skipIf

try:
    import typing_extensions
except ImportError:
    _HAS_TE = False
else:
    _HAS_TE = True

from typing_inspect_lib.core.helpers import abc as _abc

from .helpers import types_
from .helpers.build_types import _build_tests
from .helpers.type_vars import (
    CT, CT_co, CT_te, KT, T, T_co, T_contra, VT, VT_co, V_co
)

TKey = typing.TypeVar('TKey')
TValue = typing.TypeVar('TValue')
TSend = typing.TypeVar('TSend')
TReturn = typing.TypeVar('TReturn')

VERSION = sys.version_info[:3]
PY35 = VERSION[:2] == (3, 5)
PY36 = VERSION[:2] == (3, 6)
# This is because in Python 3.6.0-? and 3.5.3
# The result from `class T(List[TK][TK]):` `T[TK][int]` isn't of type List
_STOP = 3 if PY36 or VERSION == (3, 5, 3) else 4


class Types:
    LITERAL = object()
    VAR_TYPE = object()
    NEW_TYPE = object()
    NONE = object()


class BaseTestCase(TestCase):
    def plain_test(self, type_, type_class):
        if type_class is Types.LITERAL:
            self.assertEqual(types_.build_types(type_), type_)
        elif type_class is Types.VAR_TYPE:
            self.assertEqual(types_.build_types(type_), types_.VarType(type_))
        elif type_class is Types.NEW_TYPE:
            self.assertEqual(types_.build_types(type_), type_)
        elif type_class is Types.NONE:
            self.assertEqual(types_.build_types(type_), None)

    def plain_class_test(self, type_, typing_, class_, args=None, parameters=None):
        args = tuple(types_.build_types(a) for a in args or [])
        parameters = tuple(types_.build_types(p) for p in parameters or [])
        type_info = types_.Type(typing_, class_, args, parameters)
        self.assertEqual(type_info, types_.build_types(type_))

    def class_test(self, type_, typing_, class_, t_args=None, args=None, parameters=None,
                   start=0, stop=_STOP, obj=2, fn=ge):
        tests = _build_tests(type_, t_args, args, start, stop, obj, fn)
        for base, obj, special, unwrapped, args, params in tests:
            if special and unwrapped:
                params = parameters
            params = tuple(types_.build_types(p) for p in params or [])
            if not special and unwrapped and all(a in t_args for a in args):
                args = ()
            else:
                args = tuple(types_.build_types(a) for a in args)

            if special:
                type_info = types_.Type(typing_, class_, args, params)
            else:
                type_info = types_.Type(base, base, args, params)
            self.assertEqual(type_info, types_.build_types(obj))


class SpecialTestCase(BaseTestCase):
    def test_any(self):
        self.plain_test(typing.Any, Types.LITERAL)

    def test_callable(self):
        self.plain_class_test(
            typing.Callable,
            typing.Callable,
            _abc.Callable,
            []
        )
        self.plain_class_test(
            typing.Callable[[TKey], TValue],
            typing.Callable,
            _abc.Callable,
            [TKey, TValue],
            [TKey, TValue]
        )

    @skipIf(PY35 and VERSION <= (3, 5, 2),
            'ClassVar not in 3.5.[0,2]')
    def test_class_var(self):
        self.plain_class_test(
            typing.ClassVar,
            typing.ClassVar,
            typing.ClassVar,
            []
        )
        self.plain_class_test(
            typing.ClassVar[TValue],
            typing.ClassVar,
            typing.ClassVar,
            [TValue],
            [TValue]
        )

    def test_generic(self):
        self.class_test(
            typing.Generic,
            typing.Generic,
            typing.Generic,
            [TKey, TValue],
            [str, int],
            start=1,
            obj=1,
            stop=2
        )

    def test_optional(self):
        self.plain_class_test(
            typing.Optional,
            typing.Optional,
            typing.Optional,
            []
        )
        self.plain_class_test(
            typing.Optional[TValue],
            typing.Union,
            typing.Union,
            [TValue, type(None)],
            [TValue]
        )

    def test_tuple(self):
        self.class_test(
            typing.Tuple,
            typing.Tuple,
            tuple,
            [TKey, TValue],
            [str, int],
            stop=1
        )

    @skipIf(PY35 and VERSION <= (3, 5, 1),
            'Type not in 3.5.[0,1]')
    def test_type(self):
        parameters = [CT] if PY35 and VERSION <= (3, 5, 2) else [CT_co]
        self.class_test(
            typing.Type,
            typing.Type,
            type,
            [TValue],
            [int],
            parameters
        )

    def test_type_var(self):
        self.plain_test(TKey, Types.VAR_TYPE)
        self.plain_test(TValue, Types.VAR_TYPE)
        self.plain_test(TSend, Types.VAR_TYPE)
        self.plain_test(TReturn, Types.VAR_TYPE)

    def test_union(self):
        self.class_test(
            typing.Union,
            typing.Union,
            typing.Union,
            [TKey, TValue],
            [str, int],
            stop=1,
            fn=eq
        )


class ABCTestCase(BaseTestCase):
    def test_abstract_set(self):
        self.class_test(
            typing.AbstractSet,
            typing.AbstractSet,
            _abc.Set,
            [TValue],
            [int],
            [T_co]
        )

    def test_byte_string(self):
        self.class_test(
            typing.ByteString,
            typing.ByteString,
            _abc.ByteString
        )

    def test_container(self):
        self.class_test(
            typing.Container,
            typing.Container,
            _abc.Container,
            [TValue],
            [int],
            [T_co]
        )

    @skipIf(PY35 and VERSION <= (3, 5, 3),
            'ContextManager not in 3.5.[0,3]')
    def test_context_manager(self):
        self.class_test(
            typing.ContextManager,
            typing.ContextManager,
            _abc.AbstractContextManager,
            [TValue],
            [int],
            [T_co]
        )

    def test_hashable(self):
        self.class_test(
            typing.Hashable,
            typing.Hashable,
            _abc.Hashable
        )

    def test_items_view(self):
        if PY35 and VERSION <= (3, 5, 1):
            self.plain_class_test(
                typing.ItemsView,
                typing.ItemsView,
                _abc.ItemsView,
                [],
                [T_co, KT, VT_co]
            )
            self.plain_class_test(
                typing.ItemsView[TKey, TValue, TReturn],
                typing.ItemsView,
                _abc.ItemsView,
                [TKey, TValue, TReturn],
                [TKey, TValue, TReturn]
            )
        else:
            self.plain_class_test(
                typing.ItemsView,
                typing.ItemsView,
                _abc.ItemsView,
                [],
                [KT, VT_co]
            )
            self.plain_class_test(
                typing.ItemsView[TKey, TValue],
                typing.ItemsView,
                _abc.ItemsView,
                [TKey, TValue],
                [TKey, TValue]
            )

    def test_iterable(self):
        self.class_test(
            typing.Iterable,
            typing.Iterable,
            _abc.Iterable,
            [TValue],
            [int],
            [T_co]
        )

    def test_iterator(self):
        self.class_test(
            typing.Iterator,
            typing.Iterator,
            _abc.Iterator,
            [TValue],
            [int],
            [T_co]
        )

    def test_keys_view(self):
        self.class_test(
            typing.KeysView,
            typing.KeysView,
            _abc.KeysView,
            [TKey],
            [int],
            [KT]
        )

    def test_mapping(self):
        self.class_test(
            typing.Mapping,
            typing.Mapping,
            _abc.Mapping,
            [TKey, TValue],
            [int, str],
            [KT, VT_co],
            fn=eq
        )

    def test_mapping_view(self):
        self.class_test(
            typing.MappingView,
            typing.MappingView,
            _abc.MappingView,
            [TKey],
            [int],
            [T_co]
        )

    def test_mutable_mapping(self):
        self.class_test(
            typing.MutableMapping,
            typing.MutableMapping,
            _abc.MutableMapping,
            [TKey, TValue],
            [int, str],
            [KT, VT],
            fn=eq
        )

    def test_mutable_sequence(self):
        self.class_test(
            typing.MutableSequence,
            typing.MutableSequence,
            _abc.MutableSequence,
            [TValue],
            [int],
            [T]
        )

    def test_mutable_set(self):
        self.class_test(
            typing.MutableSet,
            typing.MutableSet,
            _abc.MutableSet,
            [TValue],
            [int],
            [T]
        )

    def test_sequence(self):
        self.class_test(
            typing.Sequence,
            typing.Sequence,
            _abc.Sequence,
            [TValue],
            [int],
            [T_co]
        )

    def test_sized(self):
        self.class_test(
            typing.Sized,
            typing.Sized,
            _abc.Sized
        )

    def test_values_view(self):
        self.class_test(
            typing.ValuesView,
            typing.ValuesView,
            _abc.ValuesView,
            [TValue],
            [str],
            [VT_co]
        )

    @skipIf(VERSION < (3, 5, 2), 'Awaitable requires Python 3.5.2')
    def test_awaitable(self):
        self.class_test(
            typing.Awaitable,
            typing.Awaitable,
            _abc.Awaitable,
            [TValue],
            [int],
            [T_co]
        )

    @skipIf(VERSION < (3, 5, 2), 'AsyncIterator requires Python 3.5.2')
    def test_async_iterator(self):
        self.class_test(
            typing.AsyncIterator,
            typing.AsyncIterator,
            _abc.AsyncIterator,
            [TValue],
            [int],
            [T_co]
        )

    @skipIf(VERSION < (3, 5, 2), 'AsyncIterable requires Python 3.5.2')
    def test_async_iterable(self):
        self.class_test(
            typing.AsyncIterable,
            typing.AsyncIterable,
            _abc.AsyncIterable,
            [TValue],
            [int],
            [T_co]
        )

    @skipIf(VERSION < (3, 5, 3), 'Coroutine requires Python 3.5.3')
    def test_coroutine(self):
        self.class_test(
            typing.Coroutine,
            typing.Coroutine,
            _abc.Coroutine,
            [TKey, TSend, TReturn],
            [int, str, str],
            [T_co, T_contra, V_co],
            fn=eq
        )

    @skipIf(VERSION < (3, 6, 0), 'Collection requires Python 3.6')
    def test_collection(self):
        self.class_test(
            typing.Collection,
            typing.Collection,
            _abc.Collection,
            [TValue],
            [int],
            [T_co]
        )

    @skipIf(VERSION < (3, 6, 1), 'AsyncGenerator requires Python 3.6.1')
    def test_async_generator(self):
        self.class_test(
            typing.AsyncGenerator,
            typing.AsyncGenerator,
            _abc.AsyncGenerator,
            [TKey, TSend],
            [int, str],
            [T_co, T_contra],
            fn=eq
        )

    @skipIf(
        VERSION < (3, 5, 4)
        or (PY36 and VERSION <= (3, 6, 1)),
        'AsyncContextManager requires Python 3.5.4 and not in 3.6.[0,1]')
    def test_async_context_manager(self):
        self.class_test(
            typing.AsyncContextManager,
            typing.AsyncContextManager,
            _abc.AbstractAsyncContextManager,
            [TValue],
            [int],
            [T_co]
        )


class ProtocolsTestCase(BaseTestCase):
    def test_reversible(self):
        self.class_test(
            typing.Reversible,
            typing.Reversible,
            _abc.Reversible,
            [TValue],
            [int],
            [T_co]
        )

    def test_supports_abs(self):
        self.class_test(
            typing.SupportsAbs,
            typing.SupportsAbs,
            typing.SupportsAbs,
            parameters=[T_co]
        )

    @skipIf(VERSION < (3, 0, 0), 'SupportsBytes requires Python 3.?.?')
    def test_supports_bytes(self):
        self.class_test(
            typing.SupportsBytes,
            typing.SupportsBytes,
            typing.SupportsBytes
        )

    def test_supports_complex(self):
        self.class_test(
            typing.SupportsComplex,
            typing.SupportsComplex,
            typing.SupportsComplex
        )

    def test_supports_float(self):
        self.class_test(
            typing.SupportsFloat,
            typing.SupportsFloat,
            typing.SupportsFloat
        )

    def test_supports_int(self):
        self.class_test(
            typing.SupportsInt,
            typing.SupportsInt,
            typing.SupportsInt
        )

    @skipIf(VERSION < (3, 0, 0), 'SupportsRound requires Python 3.?.?')
    def test_supports_round(self):
        self.class_test(
            typing.SupportsRound,
            typing.SupportsRound,
            typing.SupportsRound,
            parameters=[T_co]
        )


class CollectionTestCase(BaseTestCase):
    @skipIf((PY35 and VERSION <= (3, 5, 3)) or VERSION == (3, 6, 0),
            'Counter not in 3.5.[0,3] or 3.6.0')
    def test_counter(self):
        self.class_test(
            typing.Counter,
            typing.Counter,
            collections.Counter,
            [TValue],
            [int],
            [T]
        )

    @skipIf(VERSION < (3, 3, 0)
            or (PY35 and VERSION <= (3, 5, 3))
            or VERSION == (3, 6, 0),
            'ChainMap requires 3.3 and not in 3.5.[0,3] or 3.6.0')
    def test_chain_map(self):
        self.class_test(
            typing.ChainMap,
            typing.ChainMap,
            collections.ChainMap,
            [TKey, TValue],
            [int, str],
            [KT, VT],
            fn=eq
        )

    @skipIf((PY35 and VERSION <= (3, 5, 3)) or VERSION == (3, 6, 0),
            'Deque not in 3.5.[0,3] or 3.6.0')
    def test_deque(self):
        self.class_test(
            typing.Deque,
            typing.Deque,
            collections.deque,
            [TValue],
            [int],
            [T]
        )

    def test_dict(self):
        self.class_test(
            typing.Dict,
            typing.Dict,
            dict,
            [TKey, TValue],
            [int, str],
            [KT, VT],
            fn=eq
        )

    @skipIf((PY35 and VERSION <= (3, 5, 1)),
            'DefaultDict not in 3.5.[0,1]')
    def test_default_dict(self):
        self.class_test(
            typing.DefaultDict,
            typing.DefaultDict,
            collections.defaultdict,
            [TKey, TValue],
            [int, str],
            [KT, VT],
            fn=eq
        )

    def test_list(self):
        self.class_test(
            typing.List,
            typing.List,
            list,
            [TValue],
            [int],
            [T]
        )

    def test_set(self):
        self.class_test(
            typing.Set,
            typing.Set,
            set,
            [TValue],
            [int],
            [T]
        )

    def test_frozen_set(self):
        self.class_test(
            typing.FrozenSet,
            typing.FrozenSet,
            frozenset,
            [TValue],
            [int],
            [T_co]
        )

    def test_named_tuple(self):
        TestTuple = typing.NamedTuple(  # noqa: N806
            'TestTuple',
            [('key', TKey), ('value', TValue)]
        )
        self.class_test(
            typing.NamedTuple,
            typing.NamedTuple,
            typing.NamedTuple
        )
        self.plain_test(TestTuple, Types.NONE)

    @skipIf(VERSION < (3, 7, 2), 'OrderedDict requires Python 3.7.2')
    def test_ordered_dict(self):
        self.class_test(
            typing.OrderedDict,
            typing.OrderedDict,
            collections.OrderedDict,
            [TKey, TValue],
            [int, str],
            [KT, VT],
            fn=eq
        )

    def test_generator(self):
        self.class_test(
            typing.Generator,
            typing.Generator,
            _abc.Generator,
            [TValue, TSend, TReturn],
            [int, str, str],
            [T_co, T_contra, V_co],
            fn=eq
        )


class OneOffTestCase(BaseTestCase):
    def test_anystr(self):
        self.plain_test(typing.AnyStr, Types.VAR_TYPE)

    @skipIf(PY35 and VERSION <= (3, 5, 1),
            'NewType not in 3.5.[0,1]')
    def test_new_type(self):
        TestType = typing.NewType('TestType', int)  # noqa: N806
        self.plain_test(TestType, Types.NEW_TYPE)

    @skipIf((PY35 and VERSION <= (3, 5, 3))
            or (PY36 and VERSION <= (3, 6, 1)),
            'NoReturn not in 3.5.[0,3] or 3.6.[0,1]')
    def test_no_return(self):
        self.plain_test(typing.NoReturn, Types.LITERAL)

    @skipIf(PY35 and VERSION <= (3, 5, 1),
            'Text not in 3.5.[0,1]')
    def test_text(self):
        self.plain_test(typing.Text, Types.LITERAL)


@skipIf(not _HAS_TE, 'Typing extension test require it to be installed.')
class ExtensionsTestCase(BaseTestCase):
    @skipIf(VERSION < (3, 3, 0) or VERSION == (3, 5, 0),
            'te.Protocol requires Python 3 and not in 3.5.0')
    def test_protocol(self):
        proto = textwrap.dedent("""
        class TestProtocol(typing_extensions.Protocol):
            def fn(self, a: int) -> int:
                ...
        """)

        globals_ = {'typing_extensions': typing_extensions}
        exec(proto, globals_)
        TestProtocol = globals_['TestProtocol']  # noqa: N806
        self.class_test(
            typing_extensions.Protocol,
            typing_extensions.Protocol,
            typing_extensions.Protocol
        )
        self.class_test(
            TestProtocol,
            typing_extensions.Protocol,
            TestProtocol
        )

    # Special
    def test_class_var(self):
        self.plain_class_test(
            typing_extensions.ClassVar,
            typing_extensions.ClassVar,
            typing_extensions.ClassVar,
            []
        )
        self.plain_class_test(
            typing_extensions.ClassVar[TValue],
            typing_extensions.ClassVar,
            typing_extensions.ClassVar,
            [TValue],
            [TValue]
        )

    def test_type(self):
        self.class_test(
            typing_extensions.Type,
            typing_extensions.Type,
            type,
            [TValue],
            [int],
            [CT_te]
        )

    # ABCs
    def test_context_manager(self):
        self.class_test(
            typing_extensions.ContextManager,
            typing_extensions.ContextManager,
            _abc.AbstractContextManager,
            [TValue],
            [int],
            [T_co]
        )

    @skipIf(VERSION < (3, 5, 0), 'te.Awaitable requires Python 3.5')
    def test_awaitable(self):
        self.class_test(
            typing_extensions.Awaitable,
            typing_extensions.Awaitable,
            _abc.Awaitable,
            [TValue],
            [int],
            [T_co]
        )

    @skipIf(VERSION < (3, 5, 0), 'te.AsyncIterator requires Python 3.5')
    def test_async_iterator(self):
        self.class_test(
            typing_extensions.AsyncIterator,
            typing_extensions.AsyncIterator,
            _abc.AsyncIterator,
            [TValue],
            [int],
            [T_co]
        )

    @skipIf(VERSION < (3, 5, 0), 'te.AsyncIterable requires Python 3.5')
    def test_async_iterable(self):
        self.class_test(
            typing_extensions.AsyncIterable,
            typing_extensions.AsyncIterable,
            _abc.AsyncIterable,
            [TValue],
            [int],
            [T_co]
        )

    @skipIf(VERSION < (3, 5, 0), 'te.Coroutine requires Python 3.5')
    def test_coroutine(self):
        if PY35 and VERSION <= (3, 5, 1):
            parameters = [V_co, T_co, T_contra]
        else:
            parameters = [T_co, T_contra, V_co]
        self.class_test(
            typing_extensions.Coroutine,
            typing_extensions.Coroutine,
            _abc.Coroutine,
            [TKey, TSend, TReturn],
            [int, str, str],
            parameters,
            fn=eq
        )

    @skipIf(VERSION < (3, 6, 0), 'te.AsyncGenerator requires Python 3.6')
    def test_async_generator(self):
        self.class_test(
            typing_extensions.AsyncGenerator,
            typing_extensions.AsyncGenerator,
            _abc.AsyncGenerator,
            [TKey, TSend],
            [int, str],
            [T_co, T_contra],
            fn=eq
        )

    @skipIf(VERSION < (3, 5, 0), 'te.AsyncContextManager requires Python 3.5')
    def test_async_context_manager(self):
        self.class_test(
            typing_extensions.AsyncContextManager,
            typing_extensions.AsyncContextManager,
            _abc.AbstractAsyncContextManager,
            [TValue],
            [int],
            [T_co]
        )

    @skipIf(VERSION < (3, 3, 0), 'te.ChainMap requires Python 3.3')
    def test_chain_map(self):
        self.class_test(
            typing_extensions.ChainMap,
            typing_extensions.ChainMap,
            collections.ChainMap,
            [TKey, TValue],
            [int, str],
            [KT, VT],
            fn=eq
        )

    # collection
    def test_counter(self):
        self.plain_class_test(
            typing_extensions.Counter,
            typing_extensions.Counter,
            collections.Counter,
            [],
            [T]
        )
        if PY35 and VERSION <= (3, 5, 1):
            self.plain_class_test(
                typing_extensions.Counter[TValue],
                typing_extensions.Counter,
                collections.Counter,
                [TValue, int],
                [TValue]
            )
        else:
            self.plain_class_test(
                typing_extensions.Counter[TValue],
                typing_extensions.Counter,
                collections.Counter,
                [TValue],
                [TValue]
            )

    def test_deque(self):
        self.class_test(
            typing_extensions.Deque,
            typing_extensions.Deque,
            collections.deque,
            [TValue],
            [int],
            [T]
        )

    def test_default_dict(self):
        self.class_test(
            typing_extensions.DefaultDict,
            typing_extensions.DefaultDict,
            collections.defaultdict,
            [TKey, TValue],
            [int, str],
            [KT, VT],
            fn=eq
        )

    # One-off
    def test_new_type(self):
        TestType = typing_extensions.NewType('TestType', int)  # noqa: N806
        self.plain_test(TestType, Types.NEW_TYPE)

    def test_no_return(self):
        self.plain_test(typing_extensions.NoReturn, Types.LITERAL)

    def test_text(self):
        self.plain_test(typing_extensions.Text, Types.LITERAL)
