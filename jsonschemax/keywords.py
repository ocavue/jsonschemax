"""
This module store all keyword definitions except ``$id``.
"""

import itertools
import re
from typing import Any, Callable, cast

from jsonschemax.compilation import Validation
from jsonschemax.errors import InvalidSchemaError
from jsonschemax.types import (
    Callback,
    RefList,
    is_array,
    is_number,
    is_object,
    is_string,
)
from jsonschemax.utils import type_map

__all__ = ("draft7_keyword_map",)


def kw_deco(*type_checkers: Callable[[Any], bool], use_common_ref_logic=True):
    assert not (type_checkers and not use_common_ref_logic)

    def wrapper(keyword_func):
        def new_keyword_func(**kwargs) -> Callback:
            ref_list, uri, schema, value, validation = (
                kwargs["ref_list"],
                kwargs["uri"],
                kwargs["schema"],
                kwargs["value"],
                kwargs["validation"],
            )

            # > All other properties in a "$ref" object MUST be ignored.
            # > https://json-schema.org/draft-07/json-schema-core#rfc.section.8.3
            if "$ref" in schema and not ref_list:
                return lambda instance: True

            # TODO this keyword and JsonPointer.evaluate_tokens has very similar logic
            if ref_list and use_common_ref_logic:
                ref_key = ref_list[0]
                assert isinstance(ref_key, str)
                if isinstance(value, dict):
                    if ref_key in value:
                        subschema = value[ref_key]
                        validation.check_schema(subschema)
                        # TODO some cases dont't need this check
                        ref_callback = validation.evaluate(subschema, uri, ref_list[1:])
                        return ref_callback
                elif isinstance(value, list):
                    if ref_key.isdigit() and int(ref_key) < len(value):
                        subschema = value[int(ref_key)]
                        validation.check_schema(subschema)
                        # TODO some cases dont't need this check
                        ref_callback = validation.evaluate(subschema, uri, ref_list[1:])
                        return ref_callback
                raise InvalidSchemaError()

            # A keyword function decorated by this decorator will be ignored if all function in
            # type_checkers do not satisfy `type_checker(instance) is False`.

            # Most validation assertions only constrain values within a certain primitive type.
            # When the type of the instance is not of the type targeted by the keyword, the
            # instance is considered to conform to the assertion.

            # For example, the "maxLength" keyword will only restrict certain strings (that are
            # too long) from being valid. If the instance is a number, boolean, null, array, or
            # object, then it is valid against this assertion.

            # https://json-schema.org/draft-07/json-schema-validation.html#rfc.section.3.2.1
            callback = keyword_func(**kwargs)
            if type_checkers:

                def new_callback(instance) -> bool:
                    for type_checker in type_checkers:
                        if type_checker(instance):
                            return callback(instance)
                    return True

                return new_callback
            else:
                return callback

        return new_keyword_func

    return wrapper


@kw_deco()
def _definitions(
    *, value, schema: dict, uri: str, validation: Validation, ref_list: RefList
) -> Callback:
    return lambda instance: True


@kw_deco()
def _type(
    *, value, schema: dict, uri: str, validation: Validation, ref_list: RefList
) -> Callback:
    """
    type

    https://json-schema.org/draft-06/json-schema-validation.html#rfc.section.6.25
    https://json-schema.org/draft-07/json-schema-validation.html#rfc.section.6.1.1
    """
    assert isinstance(value, (str, list))
    if isinstance(value, str):

        def f(instance):
            result = type_map[value](instance)
            return result

        return f
    else:
        return lambda instance: any([type_map[v](instance) for v in value])


@kw_deco()
def _enum(
    *, value, schema: dict, uri: str, validation: Validation, ref_list: RefList
) -> Callback:
    """
    enum

    https://json-schema.org/draft-06/json-schema-validation.html#rfc.section.6.23
    https://json-schema.org/draft-07/json-schema-validation.html#rfc.section.6.1.2
    """
    assert isinstance(value, list) and len(value) >= 1

    def callback(instance):
        for item in value:
            if instance == item:
                return True
        return False

    return callback


@kw_deco()
def _const(
    *, value, schema: dict, uri: str, validation: Validation, ref_list: RefList
) -> Callback:
    """
    const

    https://json-schema.org/draft-06/json-schema-validation.html#rfc.section.6.24
    https://json-schema.org/draft-07/json-schema-validation.html#rfc.section.6.1.3
    """
    return lambda instance: instance == value


# Validation Keywords for Numeric Instances (number and integer)


@kw_deco(is_number)
def _multiple_of(
    *, value, schema: dict, uri: str, validation: Validation, ref_list: RefList
) -> Callback:
    """
    multipleOf

    https://json-schema.org/draft-06/json-schema-validation.html#rfc.section.6.1
    https://json-schema.org/draft-07/json-schema-validation.html#rfc.section.6.2.1
    """

    return lambda instance: (instance / value).is_integer()


@kw_deco(is_number)
def _maximum(
    *, value, schema: dict, uri: str, validation: Validation, ref_list: RefList
) -> Callback:
    """
    maximum

    https://json-schema.org/draft-06/json-schema-validation.html#rfc.section.6.2
    https://json-schema.org/draft-07/json-schema-validation.html#rfc.section.6.2.2
    """
    return lambda instance: instance <= value


@kw_deco(is_number)
def _exclusive_maximum(
    *, value, schema: dict, uri: str, validation: Validation, ref_list: RefList
) -> Callback:
    """
    exclusiveMaximum

    https://json-schema.org/draft-06/json-schema-validation.html#rfc.section.6.3
    https://json-schema.org/draft-07/json-schema-validation.html#rfc.section.6.2.3
    """
    return lambda instance: instance < value


@kw_deco(is_number)
def _minimum(
    *, value, schema: dict, uri: str, validation: Validation, ref_list: RefList
) -> Callback:
    """
    minimum

    https://json-schema.org/draft-06/json-schema-validation.html#rfc.section.6.4
    https://json-schema.org/draft-07/json-schema-validation.html#rfc.section.6.2.4
    """
    return lambda instance: instance >= value


@kw_deco(is_number)
def _exclusive_minimum(
    *, value, schema: dict, uri: str, validation: Validation, ref_list: RefList
) -> Callback:
    """
    exclusiveMinimum

    https://json-schema.org/draft-06/json-schema-validation.html#rfc.section.6.5
    https://json-schema.org/draft-07/json-schema-validation.html#rfc.section.6.2.5
    """
    return lambda instance: instance > value


# Validation Keywords for Strings


@kw_deco(is_string)
def _max_length(
    *, value, schema: dict, uri: str, validation: Validation, ref_list: RefList
) -> Callback:
    """
    maxLength

    https://json-schema.org/draft-06/json-schema-validation.html#rfc.section.6.6
    https://json-schema.org/draft-07/json-schema-validation.html#rfc.section.6.3.1
    """
    return lambda instance: len(cast(str, instance)) <= value


@kw_deco(is_string)
def _min_length(
    *, value, schema: dict, uri: str, validation: Validation, ref_list: RefList
) -> Callback:
    """
    minLength

    https://json-schema.org/draft-06/json-schema-validation.html#rfc.section.6.7
    https://json-schema.org/draft-07/json-schema-validation.html#rfc.section.6.3.2
    """
    return lambda instance: len(cast(str, instance)) >= value


@kw_deco(is_string)
def _pattern(
    *, value, schema: dict, uri: str, validation: Validation, ref_list: RefList
) -> Callback:
    """
    pattern

    https://json-schema.org/draft-06/json-schema-validation.html#rfc.section.6.8
    https://json-schema.org/draft-07/json-schema-validation.html#rfc.section.6.3.3
    """
    return lambda instance: bool(re.search(value, instance))


# Validation Keywords for Arrays


@kw_deco(is_array)
def _items(
    *, value, schema: dict, uri: str, validation: Validation, ref_list: RefList
) -> Callback:
    """
    items

    https://json-schema.org/draft-07/json-schema-validation.html#rfc.section.6.4.1
    https://json-schema.org/draft-06/json-schema-validation.html#rfc.section.6.9
    """
    # TODO base of value's type, there are 2 ways to check ref_list
    if isinstance(value, list):
        inner_callbacks = []
        for subschema in value:
            inner_callbacks.append(validation.evaluate(subschema, uri, ref_list))

        def callback(instance):
            for inner_callback, subinstance in zip(inner_callbacks, instance):
                if inner_callback(subinstance) is False:
                    return False
            return True

        return callback

    else:
        inner_callback = validation.evaluate(value, uri, ref_list)

        def callback(instance):
            for subinstance in instance:
                if inner_callback(subinstance) is False:
                    return False
            return True

        return callback


@kw_deco(is_array)
def _additional_items(
    *, value, schema: dict, uri: str, validation: Validation, ref_list: RefList
) -> Callback:
    """
    additionalItems

    https://json-schema.org/draft-06/json-schema-validation.html#rfc.section.6.10
    https://json-schema.org/draft-07/json-schema-validation.html#rfc.section.6.4.2
    """
    inner_callback = validation.evaluate(
        value, uri, ref_list
    )  # TODO is ref_list correct?

    def callback(instance):
        if isinstance(schema.get("items"), list):
            if len(schema["items"]) < len(instance):
                for subinstance in instance[len(schema["items"]) :]:
                    if inner_callback(subinstance) is False:
                        return False
        return True

    return callback


@kw_deco(is_array)
def _max_items(
    *, value, schema: dict, uri: str, validation: Validation, ref_list: RefList
) -> Callback:
    """
    maxItems

    https://json-schema.org/draft-06/json-schema-validation.html#rfc.section.6.11
    https://json-schema.org/draft-07/json-schema-validation.html#rfc.section.6.4.3
    """
    return lambda instance: len(cast(list, instance)) <= value


@kw_deco(is_array)
def _min_items(
    *, value, schema: dict, uri: str, validation: Validation, ref_list: RefList
) -> Callback:
    """
    minItems

    https://json-schema.org/draft-06/json-schema-validation.html#rfc.section.6.12
    https://json-schema.org/draft-07/json-schema-validation.html#rfc.section.6.4.4
    """
    return lambda instance: len(cast(list, instance)) >= value


@kw_deco(is_array)
def _unique_items(
    *, value, schema: dict, uri: str, validation: Validation, ref_list: RefList
) -> Callback:
    """
    uniqueItems

    https://json-schema.org/draft-06/json-schema-validation.html#rfc.section.6.13
    https://json-schema.org/draft-07/json-schema-validation.html#rfc.section.6.4.5
    """

    def callback(instance):
        for a, b in itertools.combinations(instance, 2):
            if type(a) == type(b) and a == b:
                return False
        return True

    return callback


@kw_deco(is_array)
def _contains(
    *, value, schema: dict, uri: str, validation: Validation, ref_list: RefList
) -> Callback:
    """
    contains

    https://json-schema.org/draft-06/json-schema-validation.html#rfc.section.6.14
    https://json-schema.org/draft-07/json-schema-validation.html#rfc.section.6.4.6
    """
    inner_callback = validation.evaluate(value, uri, ref_list)

    def callback(instance):
        for subinstance in instance:
            if inner_callback(subinstance) is True:
                return True
        return False

    return callback


# Validation Keywords for Objects


@kw_deco(is_object)
def _max_properties(
    *, value, schema: dict, uri: str, validation: Validation, ref_list: RefList
) -> Callback:
    """
    maxProperties

    https://json-schema.org/draft-06/json-schema-validation.html#rfc.section.6.15
    https://json-schema.org/draft-07/json-schema-validation.html#rfc.section.6.5.1
    """
    return lambda instance: len(cast(dict, instance).keys()) <= value


@kw_deco(is_object)
def _min_properties(
    *, value, schema: dict, uri: str, validation: Validation, ref_list: RefList
) -> Callback:
    """
    minProperties

    https://json-schema.org/draft-06/json-schema-validation.html#rfc.section.6.16
    https://json-schema.org/draft-07/json-schema-validation.html#rfc.section.6.5.2
    """
    return lambda instance: len(cast(dict, instance).keys()) >= value


@kw_deco(is_object)
def _required(
    *, value, schema: dict, uri: str, validation: Validation, ref_list: RefList
) -> Callback:
    """
    required

    https://json-schema.org/draft-06/json-schema-validation.html#rfc.section.6.17
    https://json-schema.org/draft-07/json-schema-validation.html#rfc.section.6.5.3
    """

    def callback(instance):
        assert isinstance(instance, dict)
        return all([key in instance for key in value])

    return callback


@kw_deco(is_object)
def _properties(
    *, value, schema: dict, uri: str, validation: Validation, ref_list: RefList
) -> Callback:
    """
    properties

    https://json-schema.org/draft-06/json-schema-validation.html#rfc.section.6.18
    https://json-schema.org/draft-07/json-schema-validation.html#rfc.section.6.5.4
    """
    assert not ref_list
    inner_callbacks = {}
    for key, subschema in value.items():
        inner_callbacks[key] = validation.evaluate(subschema, uri, ref_list)

    def final_callback(instance):
        for key, inner_callback in inner_callbacks.items():
            if key in instance:
                if inner_callback(instance[key]) is False:
                    return False
        return True

    return final_callback


@kw_deco(is_object)
def _pattern_properties(
    *, value, schema: dict, uri: str, validation: Validation, ref_list: RefList
) -> Callback:
    """
    patternProperties

    https://json-schema.org/draft-06/json-schema-validation.html#rfc.section.6.19
    https://json-schema.org/draft-07/json-schema-validation.html#rfc.section.6.5.5
    """
    inner_callbacks = {}
    assert not ref_list
    for key_pattern, subschema in value.items():
        inner_callbacks[key_pattern] = validation.evaluate(subschema, uri, ref_list)

    def callback(instance):
        for key_pattern, inner_callback in inner_callbacks.items():
            for key, subinstance in instance.items():
                if re.search(key_pattern, key):
                    if inner_callback(subinstance) is False:
                        return False
        return True

    return callback


@kw_deco(is_object)
def _additional_properties(
    *, value, schema: dict, uri: str, validation: Validation, ref_list: RefList
) -> Callback:
    """
    additionalProperties

    https://json-schema.org/draft-06/json-schema-validation.html#rfc.section.6.20
    https://json-schema.org/draft-07/json-schema-validation.html#rfc.section.6.5.6
    """

    f = validation.evaluate(value, uri, ref_list)

    def callback(instance):
        for key, subinstance in instance.items():

            if key in schema.get("properties", {}):
                continue

            match_pattern = False
            for key_pattern in schema.get("patternProperties", {}):
                if re.search(key_pattern, key):
                    match_pattern = True
                    break
            if match_pattern:
                continue

            result = f(subinstance)
            if result is False:
                return False
        return True

    return callback


@kw_deco(is_object)
def _dependencies(
    *, value, schema: dict, uri: str, validation: Validation, ref_list: RefList
) -> Callback:
    """
    dependencies

    https://json-schema.org/draft-06/json-schema-validation.html#rfc.section.6.21
    https://json-schema.org/draft-07/json-schema-validation.html#rfc.section.6.5.7
    """
    assert isinstance(value, dict)
    inner_callbacks = []
    for dependency_key, dependency_value in value.items():

        if isinstance(dependency_value, list):
            assert all([isinstance(i, str) for i in dependency_value])

            def inner_callback(instance):
                if dependency_key in instance:
                    for key in dependency_value:
                        if key not in instance:
                            return False
                return True

            inner_callbacks.append(inner_callback)

        else:
            assert isinstance(dependency_value, (dict, bool))
            dependency_callback = validation.evaluate(dependency_value, uri, ref_list)

            def inner_callback(instance):
                if dependency_key in instance:
                    if dependency_callback(instance) is False:
                        return False
                return True

            inner_callbacks.append(inner_callback)

    return lambda instance: all([f(instance) for f in inner_callbacks])


@kw_deco(is_object)
def _property_names(
    *, value, schema: dict, uri: str, validation: Validation, ref_list: RefList
) -> Callback:
    """
    propertyNames

    https://json-schema.org/draft-06/json-schema-validation.html#rfc.section.6.22
    https://json-schema.org/draft-07/json-schema-validation.html#rfc.section.6.5.8
    """
    inner_callback = validation.evaluate(value, uri, [])
    return lambda instance: all([inner_callback(i) for i in cast(dict, instance)])


# Keywords for Applying Subschemas Conditionally


@kw_deco()
def _if(
    *, value, schema: dict, uri: str, validation: Validation, ref_list: RefList
) -> Callback:
    """
    if

    https://json-schema.org/draft-07/json-schema-validation.html#rfc.section.6.6.1
    """
    if_callback = validation.evaluate(value, uri, ref_list)
    then_callback = validation.evaluate(schema.get("then", True), uri, ref_list)
    else_callback = validation.evaluate(schema.get("else", True), uri, ref_list)

    def callback(instance) -> bool:
        if_result = if_callback(instance)

        if if_result:
            then_result = then_callback(instance)
            return then_result
        else:
            else_result = else_callback(instance)
            return else_result

    return callback


@kw_deco()
def _then(
    *, value, schema: dict, uri: str, validation: Validation, ref_list: RefList
) -> Callback:
    """
    then

    the implementation of "then" is in the definition of "if"

    https://json-schema.org/draft-07/json-schema-validation.html#rfc.section.6.6.2
    """
    return lambda instance: True


@kw_deco()
def _else(
    *, value, schema: dict, uri: str, validation: Validation, ref_list: RefList
) -> Callback:
    """
    else

    the implementation of "else" is in the definition of "if"

    https://json-schema.org/draft-07/json-schema-validation.html#rfc.section.6.6.3
    """
    return lambda instance: True


# Keywords for Applying Subschemas With Boolean Logic


@kw_deco()
def _all_of(
    *, value, schema: dict, uri: str, validation: Validation, ref_list: RefList
) -> Callback:
    """
    allOf

    https://json-schema.org/draft-06/json-schema-validation.html#rfc.section.6.26
    https://json-schema.org/draft-07/json-schema-validation.html#rfc.section.6.7.1
    """
    assert not ref_list
    inner_callbacks = []
    for subschema in value:
        inner_callbacks.append(validation.evaluate(subschema, uri, ref_list))

    return lambda instance: all([f(instance) for f in inner_callbacks])


@kw_deco()
def _any_of(
    *, value, schema: dict, uri: str, validation: Validation, ref_list: RefList
) -> Callback:
    """
    anyOf

    https://json-schema.org/draft-06/json-schema-validation.html#rfc.section.6.27
    https://json-schema.org/draft-07/json-schema-validation.html#rfc.section.6.7.2
    """
    assert not ref_list
    inner_callbacks = []
    for subschema in value:
        inner_callbacks.append(validation.evaluate(subschema, uri, ref_list))

    return lambda instance: any([f(instance) for f in inner_callbacks])


@kw_deco()
def _one_of(
    *, value, schema: dict, uri: str, validation: Validation, ref_list: RefList
) -> Callback:
    """
    oneOf

    https://json-schema.org/draft-06/json-schema-validation.html#rfc.section.6.28
    https://json-schema.org/draft-07/json-schema-validation.html#rfc.section.6.7.3
    """
    assert not ref_list
    inner_callbacks = []
    for subschema in value:
        inner_callbacks.append(validation.evaluate(subschema, uri, ref_list))

    def callback(instance) -> bool:
        count = 0
        for inner_callback in inner_callbacks:
            if inner_callback(instance) is True:
                count += 1
        return count == 1

    return callback


@kw_deco()
def _not(
    *, value, schema: dict, uri: str, validation: Validation, ref_list: RefList
) -> Callback:
    """
    not

    https://json-schema.org/draft-06/json-schema-validation.html#rfc.section.6.29
    https://json-schema.org/draft-07/json-schema-validation.html#rfc.section.6.7.4
    """
    assert isinstance(value, (bool, dict))
    inner_callback = validation.evaluate(value, uri, ref_list)
    return lambda instance: not inner_callback(instance)


draft7_keyword_map = {
    # "$id": _id,
    # "$ref": _ref,
    "definitions": _definitions,
    "type": _type,
    "enum": _enum,
    "const": _const,
    "multipleOf": _multiple_of,
    "maximum": _maximum,
    "exclusiveMaximum": _exclusive_maximum,
    "minimum": _minimum,
    "exclusiveMinimum": _exclusive_minimum,
    "maxLength": _max_length,
    "minLength": _min_length,
    "pattern": _pattern,
    "items": _items,
    "additionalItems": _additional_items,
    "maxItems": _max_items,
    "minItems": _min_items,
    "uniqueItems": _unique_items,
    "contains": _contains,
    "maxProperties": _max_properties,
    "minProperties": _min_properties,
    "required": _required,
    "properties": _properties,
    "patternProperties": _pattern_properties,
    "additionalProperties": _additional_properties,
    "dependencies": _dependencies,
    "propertyNames": _property_names,
    "if": _if,
    "then": _then,
    "else": _else,
    "allOf": _all_of,
    "anyOf": _any_of,
    "oneOf": _one_of,
    "not": _not,
}
