"""Small unit tests for the safe arithmetic calculator."""

import unittest

from calculator import calculate


class CalculateTests(unittest.TestCase):
    def test_addition_and_precedence(self):
        self.assertEqual(calculate("2 + 3 * 4"), 14)

    def test_parentheses_and_division(self):
        self.assertEqual(calculate("(10 - 4) / 2"), 3)

    def test_unary_negative(self):
        self.assertEqual(calculate("-5 + 2"), -3)

    def test_rejects_unsupported_python(self):
        with self.assertRaises(ValueError):
            calculate("__import__('os').system('echo unsafe')")

    def test_rejects_division_by_zero(self):
        with self.assertRaises(ValueError):
            calculate("4 / 0")


if __name__ == "__main__":
    unittest.main()
