import jsonschemax

# jsonschemax.compile(
#     {"properties": {"propertyNames": {"$ref": "#"}, "enum": {"items": True}}},
#     jsonschemax.draft7_keyword_map,
# )
jsonschemax.compile(jsonschemax.draft7_meta_schema)
