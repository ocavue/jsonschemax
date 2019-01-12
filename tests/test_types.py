import math
import unittest

from jsonschemax import types


class TestTypes(unittest.TestCase):
    def test_is_array(self):
        self.assertTrue(types.is_array([]))
        self.assertTrue(types.is_array([1]))
        self.assertTrue(types.is_array([1, 2]))

        self.assertFalse(types.is_array(tuple([1, 2])))

    def test_is_boolean(self):
        self.assertTrue(types.is_boolean(True))
        self.assertTrue(types.is_boolean(False))

        self.assertFalse(types.is_boolean(1))
        self.assertFalse(types.is_boolean(0))

    def test_is_integer(self):
        self.assertTrue(types.is_integer(0))
        self.assertTrue(types.is_integer(0.0))

        self.assertTrue(types.is_integer(+1))
        self.assertTrue(types.is_integer(-1))
        self.assertTrue(types.is_integer(+1.0))
        self.assertTrue(types.is_integer(-1.0))

        self.assertFalse(types.is_integer(+math.inf))
        self.assertFalse(types.is_integer(-math.inf))

        self.assertFalse(types.is_integer(True))
        self.assertFalse(types.is_integer(False))

    def test_is_null(self):
        self.assertTrue(types.is_null(None))

        self.assertFalse(types.is_null(""))
        self.assertFalse(types.is_null(0))
        self.assertFalse(types.is_null(False))
        self.assertFalse(types.is_null([]))
        self.assertFalse(types.is_null({}))
        self.assertFalse(types.is_null("None"))

    def test_is_number(self):
        self.assertTrue(types.is_number(0))
        self.assertTrue(types.is_number(0.0))

        self.assertTrue(types.is_number(+1))
        self.assertTrue(types.is_number(-1))
        self.assertTrue(types.is_number(+1.0))
        self.assertTrue(types.is_number(-1.0))
        self.assertTrue(types.is_number(+1.1))
        self.assertTrue(types.is_number(-1.1))

        self.assertTrue(types.is_number(+math.inf))
        self.assertTrue(types.is_number(-math.inf))

        self.assertFalse(types.is_number(True))
        self.assertFalse(types.is_number(False))

    def test_is_object(self):
        pass

    def test_is_string(self):
        pass

    def test_is_any(self):
        pass


if __name__ == "__main__":
    unittest.main()
