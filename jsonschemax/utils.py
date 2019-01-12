import json
import pkgutil
import urllib.parse
from typing import Any, Callable, Dict, List, Tuple, Union
from urllib.parse import urlsplit, urlunsplit

from jsonschemax import types
from jsonschemax.errors import JsonSchemaXError

type_map: Dict[str, Callable[[Any], bool]] = {
    "null": types.is_null,
    "boolean": types.is_boolean,
    "object": types.is_object,
    "array": types.is_array,
    "number": types.is_number,
    "string": types.is_string,
    "integer": types.is_integer,
}

SchemaType: Union[Dict, str]


class JsonPointer:
    """
    A simple implement of JSON Pointer

    See also: https://tools.ietf.org/html/rfc6901
    """

    @classmethod
    def parse_json_pointer(cls, json_pointer: str) -> List[str]:
        if json_pointer in ["", "#"]:
            return []

        json_pointer = urllib.parse.unquote(json_pointer)

        if json_pointer.startswith("#"):
            json_pointer = json_pointer[1:]
        if json_pointer.startswith("/"):
            json_pointer = json_pointer[1:]

        tokens = []
        for token in json_pointer.split("/"):
            # Replace order is important
            token = token.replace("~1", "/").replace("~0", "~")
            tokens.append(token)
        return tokens

    @classmethod
    def evaluate_tokens(
        cls, json_doc, json_pointer_tokens: List[str]
    ) -> Tuple[bool, Any]:
        """
        :returns: Returns is_successful and evaluation_result
        """

        current = json_doc
        for token in json_pointer_tokens:

            if isinstance(current, dict):
                if token in current:
                    current = current[token]
                else:
                    return False, None
            elif isinstance(current, list):
                if token.isdigit() and int(token) < len(current):
                    current = current[int(token)]
                else:
                    return False, None
            else:
                return False, None

        return True, current

    @classmethod
    def evaluate(cls, json_doc, json_pointer: str) -> Tuple[bool, Any]:
        """
        A simple wrapper for ``cls.evaluate_tokens`` and ``cls.parse_json_pointer``
        """
        return cls.evaluate_tokens(json_doc, cls.parse_json_pointer(json_pointer))


def get_meta_schema(version: str) -> dict:
    allow_versions = ["draft-07"]
    if version not in allow_versions:
        raise JsonSchemaXError(
            "version must be one of {}, not {}".format(allow_versions, version)
        )
    draft_json = pkgutil.get_data("jsonschemax", "meta_schemas/{}.json".format(version))
    assert draft_json is not None
    return json.loads(draft_json.decode("utf-8"))


def run_eval_result(eval_result: Union[bool, Callable[[], bool]]) -> bool:
    assert isinstance(eval_result, bool) or callable(eval_result)
    return eval_result if isinstance(eval_result, bool) else eval_result()


def split_uri(uri):
    """split a URI into two parts: absolute-URI and fragment

    >>> split_uri('https://website.org/a/b/c?q=1#h2')
    ('https://website.org/a/b/c?q=1', 'h2')
    >>> split_uri('https://website.org/a/b/c?q=1#')
    ('https://website.org/a/b/c?q=1', '')
    >>> split_uri('https://website.org/a/b/c?q=1')
    ('https://website.org/a/b/c?q=1', '')
    >>> split_uri('#h2')
    ('', 'h2')
    """
    scheme, netloc, path, query, fragment = urlsplit(uri)
    abs_uri = urlunsplit([scheme, netloc, path, query, ""])
    return abs_uri, fragment


def always_true_callback(instance):
    return True
