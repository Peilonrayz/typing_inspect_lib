import itertools
import sys
import typing
from unittest import TestCase, skipIf

try:
    from typing_extensions import Protocol
    HAS_PROTOCOL = True
except ImportError:
    HAS_PROTOCOL = False

try:
    from typing import ClassVar
    HAS_CLASS_VAR = True
except ImportError:
    HAS_CLASS_VAR = False

from typing_inspect_lib import get_type_info, get_type_var_info
from typing_inspect_lib.core.get_base_type import get_base_type
from typing_inspect_lib.core.get_type_info import _TypeInfo
from typing_inspect_lib.core.helpers.helpers import (
    safe_contains, safe_dict_get, safe_dict_get_both, safe_getattr_tuple,
)
from typing_inspect_lib.core.helpers.compatibility import (
    abc,
    re,
    typing,
)

VERSION = sys.version_info[:3]


class BaseClassesTestCase(TestCase):
    def test_base_protocol(self):
        tests = [
            typing.SupportsInt,
            typing.SupportsFloat,
            typing.SupportsComplex,
            typing.SupportsAbs,
        ]
        if VERSION >= (3, 0, 0):
            tests.append(typing.SupportsBytes)

        for test in tests:
            self.assertEqual(
                get_base_type(test),
                (typing.Protocol, True),
                msg=str(test),
            )

    @skipIf(not HAS_PROTOCOL, 'requires protocol from typing_extensions')
    def test_protocol(self):
        class TestProtocol(Protocol):
            pass

        self.assertEqual(get_base_type(TestProtocol), (Protocol, True))

    @skipIf(not HAS_PROTOCOL, 'requires protocol from typing_extensions')
    def test_protocol_generic(self):
        T = typing.TypeVar('T')  # noqa: N806

        class TestProtocol(Protocol, typing.Generic[T]):
            pass

        self.assertEqual(get_base_type(TestProtocol), (Protocol, True))
        self.assertEqual(get_base_type(TestProtocol[int]), (Protocol, False))

    @skipIf(not HAS_PROTOCOL, 'requires protocol from typing_extensions')
    def test_generic_protocol(self):
        T = typing.TypeVar('T')  # noqa: N806

        class TestProtocol(typing.Generic[T], Protocol):
            pass

        self.assertEqual(get_base_type(TestProtocol), (Protocol, True))
        self.assertEqual(get_base_type(TestProtocol[int]), (Protocol, False))

    def test_reversible(self):
        if VERSION < (3, 6):
            self.assertEqual(
                get_base_type(typing.Reversible),
                (typing.Protocol, True),
            )
            self.assertEqual(
                get_base_type(typing.Reversible[int]),
                (typing.Protocol, False),
            )
        else:
            self.assertEqual(
                get_base_type(typing.Reversible),
                (typing.Generic, True),
            )


class TypeInfoTestCase(TestCase):
    tests = [
        typing.SupportsInt,
        int,
        typing.Mapping,
        typing.Mapping[float, int],
        typing.Pattern,
        typing.Match,
    ]
    if HAS_CLASS_VAR:
        tests.append(ClassVar)
    if HAS_PROTOCOL:
        tests.append(Protocol)

    tests = [get_type_info(t) for t in tests]

    def test_not_equal(self):
        for test_a, test_b in itertools.permutations(self.tests, 2):
            self.assertNotEqual(test_a, test_b)
            self.assertFalse(test_a == test_b)

    def test_equal(self):
        for test in self.tests:
            self.assertEqual(test, test)

    def test_not_equal_class(self):
        tests = [
            _TypeInfo(1, abc.Mapping, None, (), ()),
            _TypeInfo(1, re.Pattern, None, (), ()),
            _TypeInfo(1, re.Match, None, (), ()),
        ]
        if HAS_CLASS_VAR:
            tests.append(_TypeInfo(1, ClassVar, None, (), ()))
        if HAS_PROTOCOL:
            tests.append(_TypeInfo(1, Protocol, None, (), ()))

        for test_a, test_b in itertools.permutations(tests, 2):
            self.assertNotEqual(test_a, test_b)
            self.assertFalse(test_a == test_b)


class SafeHelpersTestCase(TestCase):
    SENTINEL = object()

    def test_dict_get(self):
        self.assertIs(safe_dict_get({}, {}, self.SENTINEL), self.SENTINEL)

    def test_dict_get_both_first(self):
        self.assertIs(safe_dict_get_both({}, {}, self.SENTINEL), self.SENTINEL)

    def test_dict_get_both_inv(self):
        class Test:
            _inv = {}

            def get(self, key, default):
                if key:
                    return {}
                else:
                    return object()

        self.assertIs(safe_dict_get_both(Test(), False, self.SENTINEL), self.SENTINEL)
        self.assertIs(safe_dict_get_both(Test(), True, self.SENTINEL), self.SENTINEL)

    def test_dict_contains(self):
        self.assertFalse(safe_contains({}, {}))

    def test_getattr_tuple(self):
        self.assertEqual(safe_getattr_tuple(object(), '__404__'), ())
        self.assertEqual(safe_getattr_tuple(object(), {}), ())


class TypeVarInfoTestCase(TestCase):
    def test_raise(self):
        with self.assertRaises(TypeError) as _:  # noqa: F841
            get_type_var_info(object())
