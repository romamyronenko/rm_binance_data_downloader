import datetime

import pytest

from rm_bdd.files_parser import _is_filename_in_date_range, str_to_datetime


class TestStrToDatetime:
    def test_monthly_format(self):
        assert str_to_datetime("2024-01") == datetime.datetime(2024, 1, 1)

    def test_daily_format(self):
        assert str_to_datetime("2024-01-15") == datetime.datetime(2024, 1, 15)

    def test_december(self):
        assert str_to_datetime("2023-12") == datetime.datetime(2023, 12, 1)

    def test_daily_end_of_month(self):
        assert str_to_datetime("2024-01-31") == datetime.datetime(2024, 1, 31)


class TestIsFilenameInDateRange:
    def test_no_bounds_always_true(self):
        assert _is_filename_in_date_range("BTCUSDT-1m-2024-01.zip", None, None) is True

    def test_from_only_inside(self):
        assert _is_filename_in_date_range("BTCUSDT-1m-2024-03.zip", "2024-01", None) is True

    def test_from_only_before(self):
        assert _is_filename_in_date_range("BTCUSDT-1m-2023-12.zip", "2024-01", None) is False

    def test_from_only_exact(self):
        assert _is_filename_in_date_range("BTCUSDT-1m-2024-01.zip", "2024-01", None) is True

    def test_to_only_inside(self):
        assert _is_filename_in_date_range("BTCUSDT-1m-2024-01.zip", None, "2024-03") is True

    def test_to_only_after(self):
        assert _is_filename_in_date_range("BTCUSDT-1m-2024-05.zip", None, "2024-03") is False

    def test_to_only_exact(self):
        assert _is_filename_in_date_range("BTCUSDT-1m-2024-03.zip", None, "2024-03") is True

    def test_both_bounds_inside(self):
        assert _is_filename_in_date_range("BTCUSDT-1m-2024-02.zip", "2024-01", "2024-03") is True

    def test_both_bounds_before_from(self):
        assert _is_filename_in_date_range("BTCUSDT-1m-2023-12.zip", "2024-01", "2024-03") is False

    def test_both_bounds_after_to(self):
        assert _is_filename_in_date_range("BTCUSDT-1m-2024-06.zip", "2024-01", "2024-03") is False

    def test_daily_filename(self):
        assert _is_filename_in_date_range("BTCUSDT-1m-2024-01-15.zip", "2024-01-01", "2024-01-31") is True

    def test_daily_outside_range(self):
        assert _is_filename_in_date_range("BTCUSDT-1m-2024-02-01.zip", "2024-01-01", "2024-01-31") is False
