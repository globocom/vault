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
        paginated_items = utils.generic_pagination(items, 1, 2)
        computed = [k for k in paginated_items]
        expected = [1, 2]
        self.assertEqual(computed, expected)
        self.assertFalse(paginated_items.has_previous())
        self.assertTrue(paginated_items.has_next())

        # Second page
        paginated_items = utils.generic_pagination(items, 2, 2)
        computed = [k for k in paginated_items]
        expected = [3, 4]
        self.assertEqual(computed, expected)
        self.assertTrue(paginated_items.has_previous())
        self.assertTrue(paginated_items.has_next())

        # Last page
        paginated_items = utils.generic_pagination(items, 3, 2)
        computed = [k for k in paginated_items]
        expected = [5, 6]
        self.assertEqual(computed, expected)
        self.assertTrue(paginated_items.has_previous())
        self.assertFalse(paginated_items.has_next())

        # If page bigger than the last page, always return last page
        paginated_items = utils.generic_pagination(items, 4, 2)
        computed = [k for k in paginated_items]
        expected = [5, 6]
        self.assertEqual(computed, expected)
