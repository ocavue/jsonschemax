import unittest

import jsonschemax


class TestInvalidSchemas(unittest.TestCase):
    def assert_invalid_schema(self, schema):
        self.assertRaises(jsonschemax.InvalidSchemaError, jsonschemax.compile, schema)

    def assert_valid_schema(self, schema):
        self.assertTrue(bool(jsonschemax.compile({"minItems": 0})))

    def test_wrong_keyword_value(self):
        self.assert_invalid_schema({"minItems": -1})
        self.assert_valid_schema({"minItems": 0})
        self.assert_valid_schema({"minItems": 1})

    def test_wrong_ref(self):
        self.assert_invalid_schema(
            {"properties": {"a": {"$ref": "#/no_exist_pointer"}}}
        )

        self.assert_invalid_schema(
            {
                "properties": {"a": {"$ref": "#/definitions/no_exist_definition"}},
                "definitions": {"int": {"type": "integer"}},
            }
        )
        self.assert_valid_schema(
            {
                "properties": {"a": {"$ref": "#/definitions/int"}},
                "definitions": {"int": {"type": "integer"}},
            }
        )

        self.assert_invalid_schema(
            {
                "properties": {"a": {"$ref": "#/myDefinitions/4"}},
                "myDefinitions": [
                    {"type": "integer"},
                    {"type": "string"},
                    {"type": "boolean"},
                ],
            }
        )
        self.assert_valid_schema(
            {
                "properties": {"a": {"$ref": "#/myDefinitions/3"}},
                "myDefinitions": [
                    {"type": "integer"},
                    {"type": "string"},
                    {"type": "boolean"},
                ],
            }
        )
