from unittest import TestCase

import typing

import typing_inspect_lib


class SpecialTestCase(TestCase):
    def test_union(self):
        self.assertEqual(typing_inspect_lib.Union, typing.Union)
