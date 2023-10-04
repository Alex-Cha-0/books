# from django.test import TestCase
from unittest import TestCase

from store.logic import operations


class LogicTestCase(TestCase):
    def test_plus(self):
        result = operations(6, 13, '+')
        self.assertEqual(19, result)

    def test_minus(self):
        result = operations(4, 4, '-')
        self.assertEqual(0, result)

    def test_multiply(self):
        result = operations(4, 4, '*')
        self.assertEqual(16, result)
