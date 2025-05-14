from datetime import UTC, datetime


class DateTimeProvider:
    @classmethod
    def utc_now(cls) -> datetime:
        """Get the current UTC time."""
        return datetime.now(UTC)


def utc_now() -> datetime:
    """
    Returns the current UTC time as a timezone-aware `datetime` object.

    IMPLEMENTATION NOTE:
        This function is defined separately to allow easy mocking in tests.
        It delegates the call to `DateTimeProvider.utc_now()` but can be overridden
        using fixtures to control datetime values in unit tests.

    Returns:
        datetime: Current UTC time with timezone info.

    Example:
        >>> utc_now()
        datetime.datetime(2025, 5, 9, 17, 45, 40, 566021, tzinfo=datetime.timezone.utc)

    """
    return DateTimeProvider.utc_now()
