from unittest import TestCase


from typing import Generic, Union, Mapping, TypeVar
try:
    import collections.abc as abc
except ImportError:
    import collections as abc

from typing_inspect_lib import get_special_type, get_typing, get_args, build_types, get_parameters, get_type_var_info


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
