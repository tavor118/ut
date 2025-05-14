# ut




[![PyPI - Version](https://img.shields.io/pypi/v/ut.svg)](https://pypi.org/project/ut)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ut.svg)](https://pypi.org/project/ut)

Helpful Python Utilities for Improved Development.

-----

# Table of Contents
* [Installation](#Installation)
* [Usage](#Usage)
	* [`@service`](#`@service`)
	* [`nget()`](#`nget()`)
	* [`destruct()`](#`destruct()`)
	* [`utc_now()`](#`utc_now()`)
* [License](#License)
* [Development](#Development)

## Installation

```console
pip install ut
```


## Usage

This package offers a range of utilities across multiple categories, including data manipulation, services, and datetime.

- `service` decorator
- `nget` function - nested get
- `destruct` function - to extract values from a dictionary, matching variable names from the caller's scope or from provided list
- `utc_now` function - returns the current UTC time as a timezone-aware datetime object.

### `@service`

`service` provides several instruments to write better services - `@service` decorator, `Break` exception and `@catch_break` decorator.

- @service

A class decorator that behaves like `@dataclass` but also logs init arguments.

This is useful for debugging or tracing how services are constructed.

Args:

    cls: The class to be decorated

Returns:

    The decorated class with dataclass features and logging

Example:

```python
@service
class UserService:
    user_id: str
    update_cache: bool = True

    def run(self):
        # Service implementation
        pass
```

- @catch_break

Decorator that gracefully handles `Break` exceptions in service operations.

Catches any `Break` exceptions raised during the execution of the decorated function,
logs the provided reason (or a default message if none is provided), and returns
`None` to indicate the operation was terminated early.

Args:

    func: The function to be decorated

Returns:

    The decorated function that handles Break exceptions

Example:

```python
@service
class DataProcessor:
    @capture_break
    def process(self, data):
        if not data:
            raise Break("Empty data provided")
        # Continue processing...
```

JUSTIFICATION OF NEED:

    There was a time when Django developers wrote business logic in views or even in templates.
    This was a poor practice, so the community found a better place for it — the model.
    This approach was called **"thin views, fat models."**
    While it works for small projects, even in medium-sized projects,
    models quickly become **God objects**, making maintenance difficult.

    To address this, developers adopted a better approach:
    moving business logic into services, which can be either functions or classes.
    This method enables the creation of reliable scenarios for use cases,
    allowing them to be used in views, Celery tasks, or even in the shell.

    Several packages provide syntactic sugar for services,
    but sometimes we need something really simple.
    That's where `ut.services` comes in.
    Let's consider the following example and refactor it using `ut`.

Before:

```python
DB = {}
class ServiceError(Exception):
    ...

@dataclass
class UserDTO:
    name: str
    age: int
    email: str

class UpdateUserService:
    user_dto: UserDTO

    def __init__(self, usr_dto: UserDTO):
        self.user_dto = usr_dto

    def run(self):
        log.info("Start creating user service")
        log.info("User DTO: %s", self.user_dto)

        if self.user_dto.email not in DB:
            log.info("User doesn't exists")
            raise ServiceError("User doesn't exists")

        user = DB[self.user_dto.email]

        if self.user_dto.name == user.name:
            log.info("User name is the same")
            return

        # update user logic
```

After:

```python
DB = {}
class ServiceError(Exception):
    ...

@dataclass
class UserDTO:
    name: str
    age: int
    email: str

@service
class UpdateUserSvc:
    user_dto: UserDTO

    @catch_break
    def run(self):
        user = self.get_user()
        self.check_name(user)
        self.update_user(user)

    def get_user(self) -> UserDTO:
        if self.user_dto.email not in DB:
            log.info("User doesn't exists")
            raise ServiceError("User doesn't exists")

        return DB[self.user_dto.email]

    def check_name(self, user: UserDTO) -> None:
        if self.user_dto.name == user.name:
            # log.info("User name is the same") <- no need - `@catch_break` will log
            raise Break("User name has the same")

    def update_user(self, user: UserDTO) -> UserDTO:
        ...
```

**Advantages of this approach:**

- **No `__init__` method** – while simple in this case, some scenarios involve processing many arguments, making this approach more flexible.
- **Clear semantics with the `@service` decorator** – it explicitly marks the class as a service, preventing confusion with `@dataclass`, which should be used for DTOs.
- **Automatic logging** – service initialization logs arguments (`args` and `kwargs`) automatically.
- **Cleaner code structure** – the `run` method contains only instructions, while business logic is encapsulated within separate methods.
- **Graceful error handling with structured logs** – operations can be interrupted cleanly with meaningful log messages.


### `nget()`

Retrieves a nested item from a dictionary, safely handling exceptions
and returning `None` if any step fails.
Useful for accessing data from a JSON.

Args:

    dct: The dictionary to traverse.
    items: A sequence of keys or indices to follow in the dictionary.
    default: The default value to return if any key/index is not found.

Returns:

    The value found at the end of the item chain, or None/default if any key/index is not found.

Example:

```python
>>> data = {'result': {'users': [{'address': {'street': 'Main St'}}]}}
>>> nget(data, 'result', 'users', 0, 'address', 'street')
'Main St'
>>> nget(data, 'result.users.0.address.street')
'Main St'
>>> nget(data, 'result', 'users', 0, 'address', 'zipcode')
None
>>> nget(data, 'result', 'users', 0, 'address', 'zipcode', default='NY')
'NY'
```


### `destruct()`

Mimics JavaScript's object destructuring.
Extract values from a dictionary, matching variable names from the caller's scope.

This function inspects the calling frame and tries to match variable names
that exist in the caller's code context with keys in the provided dictionary.
It then returns a tuple of values from the dictionary based on those variable names.

Args:

    dct: The dictionary to extract values from.
    keys: Optional sequence of keys to extract. If None, keys are inferred from the assignment statement.
    default: Default value to use when a key is not found in the dictionary. If not provided, KeyError will be raised for missing keys.

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

```python
person_dict = {"name": "John", "age": 30, "city": "New York"}

# Basic usage
name, age, city = destruct(person_dict)

# With default value for missing keys
name, age, country = destruct(person_dict, default="N/A")

# With explicit keys and default
name, country = destruct(person_dict, keys=["name", "country"], default="N/A")
```


### `utc_now()`

Returns the current UTC time as a timezone-aware `datetime` object.

IMPLEMENTATION NOTE:

    This function is defined separately to allow easy mocking in tests.
    It delegates the call to `DateTimeProvider.utc_now()` but can be overridden
    using fixtures to control datetime values in unit tests.

Example:

```python
>>> utc_now()
datetime.datetime(2025, 5, 9, 17, 45, 40, 566021, tzinfo=datetime.timezone.utc)
```

Additionally, `ut` provides a pytest fixture, `mocked_now`, which offers an in-memory implementation of `utc_now()`, enhancing test performance by eliminating unnecessary system clock access.

Example:

```python
from datetime import UTC, datetime
from unittest.mock import Mock
from ut import utc_now

class TestMockedNow:
    def test_mocked_now(self, mocked_now: Mock):
        returned_dt = mocked_now()

        assert utc_now() == returned_dt

    def test_with_provided_datetime(self, mocked_now: Mock):
        fixed_dt = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)
        mocked_now.return_value = fixed_dt

        assert utc_now() == fixed_dt
```

JUSTIFICATION OF NEED:

    There are two advantages for using `utc_now()`.
    First, it provides a convenient shortcut for retrieving the current datetime
    in the UTC timezone.
    Additionally, it can be easily replaced throughout the project if needed.

    Second, it allows us to efficiently mock the current time for testing purposes.
    Several packages provide functionality for this, including `freezegun`
    and `time-machine`.
    While `time-machine` is faster than `freezegun`, the `mocked_now` pytest fixture
    offers even better performance in tests.


## License

`ut` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.


## Development

- Installation

```bash
# Clone the repository
git clone https://github.com/tavor118/ut
cd ut

# Set up a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate

# Install the package
pip install -e .
```

- Run tests

```bash
pytest tests
```

- Linting / formatting

```bash
# run ruff
uv run ruff check .

# run ruff and fix
uv run ruff check --fix .

# format code using ruff
uv run ruff format .
```
