from typing import Callable, List, Union

JSON = Union[int, float, str, bool, dict, list, None]
Callback = Callable[[JSON], bool]
Schema = Union[bool, dict]
RefList = List[str]


def is_integer(x):
    if isinstance(x, bool):
        return False
    elif isinstance(x, int):
        return True
    elif isinstance(x, float):
        return x.is_integer()
    else:
        return False


def is_null(x):
    return x is None


def is_boolean(x):
    return isinstance(x, bool)


def is_object(x):
    return isinstance(x, dict)


def is_array(x):
    return isinstance(x, list)


def is_number(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def is_string(x):
    return isinstance(x, str)
