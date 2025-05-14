"""
Example test file showing how to use `ut` fixtures.

Note: No imports of fixtures are needed - they are automatically
discovered by pytest when the 'ut' package is installed.
"""

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
