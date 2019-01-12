class JsonSchemaXError(Exception):
    pass


class InvalidSchemaError(JsonSchemaXError):
    pass


class InvalidInstanceError(JsonSchemaXError):
    pass
