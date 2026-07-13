import os
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch


REQUIRED_SETTINGS = {
    "AWS_ACCESS_KEY": "test-access-key",
    "AWS_ACCESS_SECRET": "test-access-secret",
    "AWS_BUCKET_NAME": "test-bucket",
    "MSSQL_URL": "mssql+pymssql://user:password@localhost/test-db",
    "TEAMS_CHANNEL_URL": "https://example.invalid/teams",
    "API_URI": "https://example.invalid",
    "API_ACCOUNT": "test-account",
    "API_PASSWORD": "test-password",
    "TEAMS_WEEK_REPORT": "https://example.invalid/week-report",
}

for key, value in REQUIRED_SETTINGS.items():
    os.environ.setdefault(key, value)

from job import report


class WeekReportConnectionTests(unittest.TestCase):
    def test_session_is_closed_when_report_query_fails(self):
        session_factory = MagicMock()
        session_context = session_factory.return_value
        session_context.__enter__.return_value = MagicMock()

        with (
            patch.object(report, "SessionLocal", session_factory),
            patch.object(
                report,
                "_build_week_report_message",
                side_effect=RuntimeError("database unavailable"),
            ),
            self.assertRaisesRegex(RuntimeError, "database unavailable"),
        ):
            report.week_report.__wrapped__(datetime(2026, 7, 13, 10, 0, 0))

        session_context.__exit__.assert_called_once()


if __name__ == "__main__":
    unittest.main()
