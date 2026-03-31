import pytest

from rm_bdd.binance_metadata_manager import BinanceMetadataManager, _get_data_from_filename


class TestGetDataFromFilename:
    def test_monthly_zip(self):
        symbol, timeframe, date = _get_data_from_filename("BTCUSDT-1m-2024-01.zip")
        assert symbol == "BTCUSDT"
        assert timeframe == "1m"
        assert date == "2024-01"

    def test_daily_zip(self):
        symbol, timeframe, date = _get_data_from_filename("BTCUSDT-1m-2024-01-15.zip")
        assert symbol == "BTCUSDT"
        assert timeframe == "1m"
        assert date == "2024-01-15"

    def test_monthly_csv(self):
        symbol, timeframe, date = _get_data_from_filename("ETHUSDT-4h-2023-12.csv")
        assert symbol == "ETHUSDT"
        assert timeframe == "4h"
        assert date == "2023-12"

    def test_timeframe_with_digits(self):
        symbol, timeframe, date = _get_data_from_filename("SOLUSDT-15m-2024-06.zip")
        assert symbol == "SOLUSDT"
        assert timeframe == "15m"
        assert date == "2024-06"


class TestBinanceMetadataManager:
    def test_update_stores_date(self, tmp_path):
        bmm = BinanceMetadataManager(str(tmp_path / "meta.json"))
        bmm.update("downloads/BTCUSDT-1m-2024-01.zip")
        assert "BTCUSDT" in bmm._metadata_manager.data
        assert "2024-01" in bmm._metadata_manager.data["BTCUSDT"]["1m"]

    def test_check_returns_true_when_not_present(self, tmp_path):
        bmm = BinanceMetadataManager(str(tmp_path / "meta.json"))
        assert bmm.check("downloads/BTCUSDT-1m-2024-01.zip") is True

    def test_check_returns_false_after_update(self, tmp_path):
        bmm = BinanceMetadataManager(str(tmp_path / "meta.json"))
        bmm.update("downloads/BTCUSDT-1m-2024-01.zip")
        assert bmm.check("downloads/BTCUSDT-1m-2024-01.zip") is False

    def test_check_daily_skipped_if_month_present(self, tmp_path):
        bmm = BinanceMetadataManager(str(tmp_path / "meta.json"))
        bmm.update("downloads/BTCUSDT-1m-2024-01.zip")
        assert bmm.check("downloads/BTCUSDT-1m-2024-01-15.zip") is False

    def test_check_different_symbol_independent(self, tmp_path):
        bmm = BinanceMetadataManager(str(tmp_path / "meta.json"))
        bmm.update("downloads/BTCUSDT-1m-2024-01.zip")
        assert bmm.check("downloads/ETHUSDT-1m-2024-01.zip") is True
