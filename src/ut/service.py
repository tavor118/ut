import logging
from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Self, Type, TypeVar

log = logging.getLogger(__name__)

T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])


class Break(Exception):  # noqa: N818
    """
    Exception raised to terminate a service operation early.

    Acts as an analogue of the 'break' statement in a loop,
    but for service operations.
    It can include an optional reason message to explain why the operation was terminated.
    """


def service(cls: Type[T]) -> Type[T]:
    """
    A class decorator that behaves like `@dataclass` but also logs init arguments.

    This is useful for debugging or tracing how services are constructed.

    Args:
        cls: The class to be decorated

    Returns:
        The decorated class with dataclass features and logging

    Example:
        @service
        class UserService:
            user_id: str
            update_cache: bool = True

            def run(self):
                # Service implementation
                pass

    """
    cls = dataclass(cls)

    original_init = cls.__init__  # save original __init__ to wrap it

    @wraps(original_init)
    def init(self: Self, *args: Any, **kwargs: Any) -> None:
        log.debug("Initializing '%s' with args=%s, kwargs=%s", cls.__name__, args, kwargs)
        original_init(self, *args, **kwargs)

    cls.__init__ = init
    return cls


def catch_break(func: F) -> F:
    """
    Decorator that gracefully handles `Break` exceptions in service operations.

    Catches any `Break` exceptions raised during the execution of the decorated function,
    logs the provided reason (or a default message if none is provided), and returns
    `None` to indicate the operation was terminated early.

    Args:
        func: The function to be decorated

    Returns:
        The decorated function that handles Break exceptions

    Example:
        @service
        class DataProcessor:
            @capture_break
            def process(self, data):
                if not data:
                    raise Break("Empty data provided")
                # Continue processing...
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except Break as e:
            reason = str(e) or "Reason not provided"
            log.debug("Break svc operation. Reason: '%s'", reason)
            return None

    return wrapper
