import unittest

from jsonschemax.utils import JsonPointer


class JSONPointerTestCase(unittest.TestCase):
    def test_rfc6901(self):
        # test cases below are copied from https://tools.ietf.org/html/rfc6901

        doc = {
            "foo": ["bar", "baz"],
            "": 0,
            "a/b": 1,
            "c%d": 2,
            "e^f": 3,
            "g|h": 4,
            "i\\j": 5,
            'k"l': 6,
            " ": 7,
            "m~n": 8,
        }

        for pointer, expected_result in [
            ("", doc),
            ("/foo", ["bar", "baz"]),
            ("/foo/0", "bar"),
            ("/", 0),
            ("/a~1b", 1),
            ("/c%d", 2),
            ("/e^f", 3),
            ("/g|h", 4),
            ("/i\\j", 5),
            ('/k"l', 6),
            ("/ ", 7),
            ("/m~0n", 8),
        ]:
            with self.subTest(pointer=pointer, result=expected_result):
                is_resolved, actual_result = JsonPointer.evaluate(doc, pointer)
                self.assertTrue(is_resolved)
                self.assertEqual(expected_result, actual_result)

        for pointer, expected_result in [
            ("#", doc),
            ("#/foo", ["bar", "baz"]),
            ("#/foo/0", "bar"),
            ("#/", 0),
            ("#/a~1b", 1),
            ("#/c%25d", 2),
            ("#/e%5Ef", 3),
            ("#/g%7Ch", 4),
            ("#/i%5Cj", 5),
            ("#/k%22l", 6),
            ("#/%20", 7),
            ("#/m~0n", 8),
        ]:
            with self.subTest(pointer=pointer, result=expected_result):
                is_resolved, actual_result = JsonPointer.evaluate(doc, pointer)
                self.assertTrue(is_resolved)
                self.assertEqual(expected_result, actual_result)

    def test_escape(self):
        """
        RFC 6901:

        By performing the substitutions in this order, an
        implementation avoids the error of turning '~01' first into
        '~1' and then into '/', which would be incorrect (the string
        '~01' correctly becomes '~1' after transformation).
        """

        is_resolved, result = JsonPointer.evaluate({"~1": 1, "/": 2}, "~01")
        self.assertTrue(is_resolved)
        self.assertEqual(result, 1)
