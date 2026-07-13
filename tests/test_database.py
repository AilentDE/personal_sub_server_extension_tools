import os
import unittest
from unittest.mock import patch


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

from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool

from config.database import create_database_engine
from config.setting import Settings


class DatabaseConfigurationTests(unittest.TestCase):
    def settings_arguments(self):
        return {
            "aws_access_key": "test-access-key",
            "aws_access_secret": "test-access-secret",
            "aws_bucket_name": "test-bucket",
            "mssql_url": "mssql+pymssql://user:password@localhost/test-db",
            "teams_channel_url": "https://example.invalid/teams",
            "api_uri": "https://example.invalid",
            "api_account": "test-account",
            "api_password": "test-password",
            "teams_week_report": "https://example.invalid/week-report",
        }

    def test_pool_recycle_defaults_to_1800_seconds(self):
        settings = Settings(_env_file=None, **self.settings_arguments())

        self.assertEqual(settings.db_pool_recycle_seconds, 1800)

    def test_pool_recycle_can_be_overridden_by_environment(self):
        with patch.dict(os.environ, {"DB_POOL_RECYCLE_SECONDS": "900"}):
            settings = Settings(_env_file=None, **self.settings_arguments())

        self.assertEqual(settings.db_pool_recycle_seconds, 900)

    @patch("config.database.create_engine")
    def test_engine_enables_stale_connection_protection(self, create_engine_mock):
        expected_engine = object()
        create_engine_mock.return_value = expected_engine

        result = create_database_engine("mssql+pymssql://db", 1800)

        self.assertIs(result, expected_engine)
        create_engine_mock.assert_called_once_with(
            "mssql+pymssql://db",
            pool_pre_ping=True,
            pool_recycle=1800,
            pool_use_lifo=True,
        )

    def test_pre_ping_replaces_a_stale_pooled_connection(self):
        test_engine = create_engine(
            "sqlite://",
            poolclass=QueuePool,
            pool_pre_ping=True,
        )
        self.addCleanup(test_engine.dispose)

        with test_engine.connect() as connection:
            stale_connection = connection.connection.driver_connection

        stale_connection.close()

        with test_engine.connect() as connection:
            replacement_connection = connection.connection.driver_connection
            result = connection.execute(text("SELECT 1")).scalar_one()

        self.assertEqual(result, 1)
        self.assertIsNot(replacement_connection, stale_connection)


if __name__ == "__main__":
    unittest.main()
