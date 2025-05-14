from datetime import UTC, datetime
from unittest.mock import Mock

from pytest import MonkeyPatch, fixture

from ut.utc_now import DateTimeProvider

DEFAULT_NOW = datetime(2025, 6, 6, 12, 0, 0, tzinfo=UTC)


@fixture
def mocked_now(monkeypatch: MonkeyPatch) -> Mock:
    """
    Fixture for mocking the `utc_now()` function.

    Replaces the `utc_now()` method with a mock that returns
    a predefined datetime (`DEFAULT_NOW`).

    Usage:
    - To modify the returned datetime, update the `return_value` attribute of the mock.
    >>> mocked_now.return_value = datetime(2025, 6, 6, 12, 0, 0, tzinfo=UTC)

    Returns:
        Mock: A mock instance that simulates the `utc_now()` method.
    """
    fake_utc_now = Mock(return_value=DEFAULT_NOW)
    monkeypatch.setattr(DateTimeProvider, "utc_now", fake_utc_now)

    return fake_utc_now
