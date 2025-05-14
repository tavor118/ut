import inspect
import re
from collections.abc import Sequence
from types import FrameType
from typing import Any, Dict, List, Optional, Tuple, Union


class DestructError(Exception):
    """Custom exception for errors in the destruct function."""


def _extract_variable_names(call_line: str) -> List[str]:
    """
    Extracts variable names from the caller's assignment statement:
    `name, age, city = destruct(person_dict)` -> ['name', 'age', 'city']
    """
    assignment_split = call_line.split("=")[0]  # take only the part before '='

    pattern = r"\b([a-zA-Z_]\w*)\b"
    # \b              # Word boundary to ensure capturing whole variable names
    #                 # (avoids partial matches)
    # ([a-zA-Z_]\w*)  # Captures valid Python identifiers:
    #                 # - Must start with a letter or underscore
    #                 # - Can be followed by letters, digits, or underscores
    # \b              # Another word boundary to ensure correct variable isolation

    return re.findall(pattern, assignment_split)


def _get_var_names(frame: Optional[FrameType]) -> Sequence[str]:
    """Get variables' names from a given frame."""
    if not frame:
        msg = "Failed to access a frame."
        raise DestructError(msg)

    caller_frame = frame.f_back
    if not caller_frame:
        msg = "Failed to access caller's frame."
        raise DestructError(msg)

    # get the context from the caller's frame
    code_context = inspect.getframeinfo(caller_frame).code_context
    if not code_context:
        msg = "Failed to retrieve code context."
        raise DestructError(msg)

    # get the line that called 'destruct' function
    call_line = code_context[0].strip()
    if "=" not in call_line:
        msg = "Assignment statement was not found."
        raise DestructError(msg)

    return _extract_variable_names(call_line)


def destruct(
    dct: Dict[str, Any],
    keys: Optional[Sequence[str]] = None,
    default: Any = ...,
) -> Union[Any, Tuple[Any, ...]]:
    """
    Mimics JavaScript's object destructuring.
    Extract values from a dictionary, matching variable names from the caller's scope.

    This function inspects the calling frame and tries to match variable names
    that exist in the caller's code context with keys in the provided dictionary.
    It then returns a tuple of values from the dictionary based on those variable names.

    Args:
        dct: The dictionary to extract values from.
        keys: Optional sequence of keys to extract.
            If None, keys are inferred from the assignment statement.
        default: Default value to use when a key is not found in the dictionary.
            If not provided, KeyError will be raised for missing keys.

    Returns:
        Single value or a tuple of values from the dictionary corresponding
        to the caller's variable names.

    Raises:
        KeyError: If any variable name from the caller is not found in the dictionary
            and default value is provided.
        DestructError: If the function cannot complete successfully.

    WARNING:
        `destruct` relies on inspecting the caller's frame, which may not work properly
        in interactive environments like the Python shell or Jupyter notebooks.
        Use `keys` argument if you need to work in the shell.

    Example:
        person_dict = {"name": "John", "age": 30, "city": "New York"}

        # Basic usage
        name, age, city = destruct(person_dict)

        # With default value for missing keys
        name, age, country = destruct(person_dict, default="N/A")

        # With explicit keys and default
        name, country = destruct(person_dict, keys=["name", "country"], default="N/A")
    """
    if not keys:
        frame = inspect.currentframe()
        keys = _get_var_names(frame)

    default_provided = default is not ...
    if default_provided:
        if len(keys) == 1:
            return dct.get(keys[0], default)

        return tuple(dct.get(key, default) for key in keys)

    missing = [k for k in keys if k not in dct]
    if missing:
        msg = f"Key(s) {missing} not found in dictionary."
        raise KeyError(msg)

    if len(keys) == 1:
        return dct[keys[0]]

    return tuple(dct[key] for key in keys)
