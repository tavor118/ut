from collections.abc import Mapping, Sequence
from typing import Any, TypeVar, Union, overload

T = TypeVar("T")
KeyType = Union[str, int]
NestedDict = Union[Mapping[Any, Any], Sequence[Any]]


@overload
def nget(dct: NestedDict, *items: KeyType, default: T) -> T: ...


@overload
def nget(dct: NestedDict, *items: KeyType) -> object: ...


def nget(dct: NestedDict, *items: KeyType, default: T = None) -> T | None:
    """
    Nested get.
    Retrieves a nested item from a dictionary, safely handling exceptions
    and returning None if any step fails.
    Useful for accessing data from a JSON.

    Args:
        dct: The dictionary to traverse.
        items: A sequence of keys or indices to follow in the dictionary.
        default: The default value to return if any key/index is not found.

    Returns:
        The value found at the end of the item chain, or None/default
        if any key/index is not found.

    Example:
        >>> data = {'result': {'users': [{'address': {'street': 'Main St'}}]}}
        >>> nget(data, 'result', 'users', 0, 'address', 'street')
        'Main St'
        >>> nget(data, 'result.users.0.address.street')
        'Main St'
        >>> nget(data, 'result', 'users', 0, 'address', 'zipcode')
        None
        >>> nget(data, 'result', 'users', 0, 'address', 'zipcode', default='NY')
        'NY'
    """
    keys: list[KeyType] = []

    for item in items:
        if isinstance(item, str) and "." in item:
            parts = item.split(".")
            for part in parts:
                # Convert numeric strings to integers for list indexing
                if part.isdigit():
                    keys.append(int(part))
                else:
                    keys.append(part)
        else:
            keys.append(item)

    for key in keys:
        try:
            dct = dct[key]
        except (KeyError, IndexError, TypeError):
            return default

    return dct
