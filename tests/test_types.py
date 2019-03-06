from unittest import TestCase

import typing

import typing_inspect_lib


class SpecialTestCase(TestCase):
    def test_union(self):
        self.assertEqual(typing_inspect_lib.Union, typing.Union)

    def test_run_in_subversions(self):
        self.assertEqual(typing.NoReturn, typing.NoReturn)
