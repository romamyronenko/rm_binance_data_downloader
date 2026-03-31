from unittest.mock import AsyncMock, call

import pytest

from rm_bdd.data_manager import DataManager


@pytest.fixture
def manager():
    downloader = AsyncMock()
    extractor = AsyncMock()
    formatter = AsyncMock()
    return DataManager(downloader, extractor, formatter), downloader, extractor, formatter


class TestDataManager:
    async def test_calls_all_three_stages(self, manager):
        dm, downloader, extractor, formatter = manager
        await dm.download_and_save("BTCUSDT", "1m")

        downloader.download.assert_called_once()
        extractor.extract.assert_called_once()
        formatter.format.assert_called_once()

    async def test_passes_symbol_and_timeframe(self, manager):
        dm, downloader, extractor, formatter = manager
        await dm.download_and_save("ETHUSDT", "4h")

        downloader.download.assert_called_once_with("ETHUSDT", "4h", date_from=None, date_to=None)
        extractor.extract.assert_called_once_with("ETHUSDT", "4h", date_from=None, date_to=None)
        formatter.format.assert_called_once_with("ETHUSDT", "4h", date_from=None, date_to=None)

    async def test_passes_date_range(self, manager):
        dm, downloader, extractor, formatter = manager
        await dm.download_and_save("BTCUSDT", "1m", date_from="2024-01", date_to="2024-03")

        downloader.download.assert_called_once_with(
            "BTCUSDT", "1m", date_from="2024-01", date_to="2024-03"
        )
        extractor.extract.assert_called_once_with(
            "BTCUSDT", "1m", date_from="2024-01", date_to="2024-03"
        )
        formatter.format.assert_called_once_with(
            "BTCUSDT", "1m", date_from="2024-01", date_to="2024-03"
        )

    async def test_stages_run_in_order(self, manager):
        dm, downloader, extractor, formatter = manager
        call_order = []
        downloader.download.side_effect = lambda *a, **kw: call_order.append("download")
        extractor.extract.side_effect = lambda *a, **kw: call_order.append("extract")
        formatter.format.side_effect = lambda *a, **kw: call_order.append("format")

        await dm.download_and_save("BTCUSDT", "1m")

        assert call_order == ["download", "extract", "format"]
