from typing import Callable, Dict, List, Union
from urllib.parse import urljoin

from jsonschemax.errors import InvalidSchemaError
from jsonschemax.meta_schemas import draft7_meta_schema
from jsonschemax.types import Callback, RefList, Schema
from jsonschemax.utils import JsonPointer, split_uri


class Validation:  # TODO rename: Compilation
    def __init__(self,):
        self.__is_initting = False

    def init(
        self,
        *,
        schema: Union[bool, dict],
        keyword_map: Dict[str, Callable[..., Callback]],
        check_schema: bool,
        global_schema_map: Dict[str, Schema],
        global_validation_map: Dict[str, "Validation"],
        ref_list: RefList = None,
    ):
        self.__is_initting = True

        self.__check_schema = check_schema
        self.check_schema(schema)

        if isinstance(schema, dict) and "$id" in schema:
            self.__root_id = schema["$id"]
            root_abs_uri, _ = split_uri(self.__root_id)
            if root_abs_uri:
                assert (
                    root_abs_uri not in global_schema_map
                    or global_schema_map[root_abs_uri] == schema
                )
                global_schema_map[root_abs_uri] = schema
        else:
            self.__root_id = ""

        self.__root_schema = schema
        self.__keyword_map = keyword_map
        self.__check_schema = check_schema
        self.__global_schema_map = global_schema_map  # TODO check remote schema
        self.__global_validation_map = global_validation_map

        self.__callback = self.evaluate(
            schema=self.__root_schema,
            base_uri=self.__root_id,
            ref_list=ref_list or [],
            is_root_evaluate=True,
        )

        self.__is_initting = False

    def evaluate(  # TODO rename: resolve
        self, schema, base_uri: str, ref_list: RefList, is_root_evaluate: bool = False
    ) -> Callback:
        assert self.__is_initting
        assert isinstance(base_uri, str)

        if isinstance(schema, bool):
            return lambda instance: schema
        else:
            assert isinstance(schema, dict)

            current_uri: str = (
                urljoin(base_uri, schema["$id"]) if schema.get("$id") else base_uri
            )

            # avoid circular imports
            from jsonschemax.keywords import draft7_keyword_map

            if "$ref" in schema and not ref_list:
                # return a Validation object
                ref_uri = urljoin(current_uri, schema["$ref"])
                if ref_uri not in self.__global_validation_map:
                    ref_abs_uri, ref_fragment = split_uri(ref_uri)
                    ref_schema = (
                        self.__global_schema_map[ref_abs_uri]
                        if ref_abs_uri
                        else self.__root_schema
                    )
                    validation = Validation()
                    self.__global_validation_map[ref_uri] = validation
                    validation.init(
                        schema=ref_schema,
                        check_schema=False,
                        ref_list=JsonPointer.parse_json_pointer(ref_fragment),
                        keyword_map=draft7_keyword_map,
                        global_schema_map=self.__global_schema_map,
                        global_validation_map=self.__global_validation_map,
                    )
                return self.__global_validation_map[ref_uri]

            elif "$ref" not in schema and not ref_list:
                # return a function
                inner_callbacks: List[Callback] = []
                for keyword_name, value in schema.items():
                    if keyword_name not in self.__keyword_map:
                        # > A JSON Schema MAY contain properties which are not
                        # > schema keywords. Unknown keywords SHOULD be ignored.
                        # > http://json-schema.org/draft-07/json-schema-core.html#rfc.section.4.3.1
                        continue
                    keywork_func = self.__keyword_map[keyword_name]
                    inner_callback = keywork_func(
                        value=value,
                        schema=schema,
                        uri=current_uri,
                        validation=self,
                        ref_list=[],
                    )
                    inner_callbacks.append(inner_callback)
                return lambda instance: all([f(instance) for f in inner_callbacks])

            else:
                assert ref_list
                ref_key: str = ref_list[0]
                if ref_key in self.__keyword_map and ref_key in schema:
                    # In this case, the target of "$ref" is in an schema, so
                    # we let keyword handler it.
                    keyword_func = self.__keyword_map[ref_key]
                    ref_callback = keyword_func(
                        value=schema[ref_key],
                        schema=schema,
                        uri=current_uri,
                        validation=self,
                        ref_list=ref_list[1:],
                    )
                    return ref_callback
                else:
                    # In this case, ``schema[ref_key]`` is considered as an
                    # schema if and only if ``ref_key`` has only one item.
                    # Otherwise, ``schema[ref_key]`` is just a normal json
                    # document and we should ignore ``schema[ref_key]``'s
                    # special keyword like "$id" or "$ref".

                    # So what we do here is just go thought ``schema`` and
                    # find the finaly target of "$ref".
                    # TODO check ref_schema, since meta-schema can't check it
                    is_resolved, ref_schema = JsonPointer.evaluate_tokens(
                        schema, ref_list
                    )
                    if is_resolved:
                        return self.evaluate(
                            schema=ref_schema, base_uri=current_uri, ref_list=[]
                        )
                    else:
                        raise InvalidSchemaError()

    def check_schema(self, schema):
        if self.__check_schema:
            from jsonschemax.meta_validation import draft7_validation

            if not draft7_validation(schema):
                raise InvalidSchemaError("InvalidSchema")

    def __call__(self, instance):
        return self.__callback(instance)

    @property
    def schema(self):
        return self.__root_schema


def compile(  # TODO u can't name it "compile" since Python already has a "compile" function
    schema,
    *,
    keyword_map: dict = None,
    remote_schemas: Dict[str, Schema] = None,
    check_schema: bool = True,
):
    assert isinstance(schema, (dict, bool))  # TODO Friendly error
    from jsonschemax.keywords import draft7_keyword_map  # avoid circular imports

    global_schema_map: Dict[str, Schema] = {
        "http://json-schema.org/draft-07/schema": draft7_meta_schema,
        **(remote_schemas or {}),
    }

    validation = Validation()
    validation.init(
        schema=schema,
        keyword_map=keyword_map or draft7_keyword_map,
        check_schema=check_schema,
        global_schema_map=global_schema_map,
        global_validation_map={},
    )
    return validation
