from unittest import TestCase, skipIf

import sys
from typing import Generic, Union, Mapping, TypeVar, Sequence, Sized, Iterable, Container
import typing
try:
    import collections.abc as abc
except ImportError:
    import collections as abc

from typing_inspect_lib import get_special_type, get_typing, get_args, build_types, get_parameters, get_type_var_info, get_mro, get_bases, get_mro_orig

VERSION = sys.version_info[:3]


class SpecialTestCase(TestCase):
    def test_get_special_type(self):
        self.assertEqual(Generic, get_special_type(Generic))
        self.assertEqual(Union, get_special_type(Union))

    def test_get_typing(self):
        typing_, class_ = get_typing(Mapping[str, int])
        self.assertEqual(Mapping, typing_)
        self.assertEqual(abc.Mapping, class_)

        typing_, class_ = get_typing(Union[str, int])
        self.assertEqual(Union, typing_)
        self.assertEqual(Union, class_)

    def test_get_args(self):
        self.assertEqual((), get_args(Mapping))
        self.assertEqual((str, int), get_args(Mapping[str, int]))
        self.assertEqual((Union[str, int], int), get_args(Mapping[Union[str, int], int]))

    def test_get_parameters(self):
        TKey = TypeVar('TKey')
        TValue = TypeVar('TValue')

        self.assertEqual((), get_parameters(Mapping[str, int]))
        self.assertEqual((TKey, TValue), get_parameters(Mapping[TKey, TValue]))

    def test_get_type_var_info(self):
        TExample = TypeVar('TExample', bound=int)
        t_example = get_type_var_info(TExample)

        self.assertEqual(('TExample', int, False, False), t_example)
        self.assertEqual('TExample', t_example.name)
        self.assertEqual(int, t_example.bound)
        self.assertFalse(t_example.covariant)
        self.assertFalse(t_example.contravariant)

        # Using this with typing objects
        self.assertNotEqual((), get_parameters(Mapping))
        mapping_parameters = tuple(get_type_var_info(p) for p in get_parameters(Mapping))
        self.assertEqual((('KT', None, False, False), ('VT_co', None, True, False)), mapping_parameters)

    def test_build_types(self):
        type_ = build_types(Mapping[Union[str, int], int])
        self.assertEqual(Mapping, type_.typing)
        self.assertEqual(abc.Mapping, type_.class_)
        self.assertEqual(Union, type_.args[0].typing)
        self.assertEqual(str, type_.args[0].args[0].typing)

    def test_bases(self):
        if VERSION[:2] == (3, 5) and VERSION < (3, 6, 0):
            mro = (
                (Sized, abc.Sized, None),
                (Iterable, abc.Iterable, Iterable[int]),
                (Container, abc.Container, Container[int]),
                (Generic, Generic, None)
            )
        elif VERSION < (3, 6, 0):
            mro = (
                (Sized, abc.Sized, None),
                (Iterable, abc.Iterable, Iterable[int]),
                (Container, abc.Container, Container[int])
            )
        else:
            mro = (
                (typing.Collection, abc.Collection, typing.Collection[int]),
            )

        base_mro = tuple((t, c, None) for t, c, _ in mro)
        self.assertEqual(get_bases(Mapping), base_mro)
        self.assertEqual(get_bases(abc.Mapping), base_mro)
        self.assertEqual(get_bases(Mapping[int, str]), mro)

    def test_bases_custom(self):
        class T(Mapping[int, str], Sequence[str]):
            pass

        if VERSION < (3, 7, 0):
            bases = (
                (Mapping, abc.Mapping, Mapping[int, str]),
                (Sequence, abc.Sequence, Sequence[str]),
            )
        else:
            bases = (
                (Mapping, abc.Mapping, Mapping[int, str]),
                (Sequence, abc.Sequence, Sequence[str]),
                (Generic, Generic, None)
            )

        self.assertEqual(bases, get_bases(T))

    def test_mro(self):
        if VERSION < (3, 6, 0):
            mro = (
                abc.Mapping,
                abc.Sized,
                abc.Iterable,
                abc.Container,
                object
            )
        else:
            mro = (
                abc.Mapping,
                abc.Collection,
                abc.Sized,
                abc.Iterable,
                abc.Container,
                object
            )
        self.assertEqual(get_mro(Mapping), mro)
        self.assertEqual(get_mro(abc.Mapping), mro)
        self.assertEqual(get_mro(Mapping[int, str]), mro)

    def test_mro_custom(self):
        class T(Mapping[int, str], Sequence[str]):
            pass

        if VERSION < (3, 6, 0):
            bases = (
                T,
                abc.Mapping,
                abc.Sequence,
                abc.Sized,
                abc.Iterable,
                abc.Container,
                Generic,
                object
            )
        else:
            bases = (
                T,
                abc.Mapping,
                abc.Sequence,
                abc.Reversible,
                abc.Collection,
                abc.Sized,
                abc.Iterable,
                abc.Container,
                Generic,
                object
            )

        self.assertEqual(bases, get_mro(T))

    @skipIf(True, 'Not working')
    def test_mro_orig(self):
        if VERSION < (3, 6, 0):
            mro = (
                (Mapping, abc.Mapping, Mapping[int, str]),
                (Sized, abc.Sized, None),
                (Iterable, abc.Iterable, Iterable[int]),
                (Container, abc.Container, Container[int]),
                (object, object, None)
            )
        else:
            mro = (
                (Mapping, abc.Mapping, Mapping[int, str]),
                (typing.Collection, abc.Collection, typing.Collection[int]),
                (Sized, abc.Sized, None),
                (Iterable, abc.Iterable, Iterable[int]),
                (Container, abc.Container, Container[int]),
                (object, object, None)
            )

        base_mro = tuple((t, c, None) for t, c, _ in mro)
        self.assertEqual(get_mro_orig(Mapping), base_mro)
        self.assertEqual(get_mro_orig(abc.Mapping), base_mro)
        self.assertEqual(get_mro_orig(Mapping[int, str]), mro)

    def test_mro_orig_custom(self):
        return
        class T(Mapping[int, str], Sequence[str]):
            pass

        if VERSION < (3, 6, 0):
            bases = (
                T,
                abc.Mapping,
                abc.Sequence,
                abc.Sized,
                abc.Iterable,
                abc.Container,
                Generic,
                object
            )
        else:
            bases = (
                T,
                abc.Mapping,
                abc.Sequence,
                abc.Reversible,
                abc.Collection,
                abc.Sized,
                abc.Iterable,
                abc.Container,
                Generic,
                object
            )

        self.assertEqual(bases, get_mro_orig(T))
