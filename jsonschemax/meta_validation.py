from jsonschemax.compilation import compile
from jsonschemax.keywords import draft7_keyword_map
from jsonschemax.meta_schemas import draft7_meta_schema

draft7_validation = compile(
    schema=draft7_meta_schema, keyword_map=draft7_keyword_map, check_schema=False
)
