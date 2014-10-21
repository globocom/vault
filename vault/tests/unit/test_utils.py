# -*- coding:utf-8 -*-
"""
Unit tests for utils functions
"""

from unittest import TestCase

from vault import utils

class TestVaultUtils(TestCase):

    def test_generic_pagination(self):
        items = [1, 2, 3, 4, 5, 6]

        # First page
        computed = utils.generic_pagination(items, 1, 2)
        expected = [1, 2]
        self.assertEqual(computed, expected)

        # Second page
        computed = utils.generic_pagination(items, 2, 2)
        expected = [3, 4]
        self.assertEqual(computed, expected)

        # Last page
        computed = utils.generic_pagination(items, 3, 2)
        expected = [5, 6]
        self.assertEqual(computed, expected)

        # If page bigger than the last page, always return last page
        computed = utils.generic_pagination(items, 4, 2)
        expected = [5, 6]
        self.assertEqual(computed, expected)
