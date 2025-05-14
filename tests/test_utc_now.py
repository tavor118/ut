from datetime import UTC, datetime

from ut import utc_now


class TestUTCNow:
    def test_utc_now(self):
        now = utc_now()

        assert isinstance(now, datetime)
        assert now.tzinfo == UTC

        assert now.date() == datetime.now(UTC).date()
