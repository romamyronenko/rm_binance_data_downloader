"""
Тести на логування — перевіряють що потрібні повідомлення справді з'являються
і не з'являються у правильних ситуаціях.
"""
import logging
import zipfile
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from rm_bdd.data_downloader import DataDownloader, download_file
from rm_bdd.data_extractor import DataExtractor
from rm_bdd.data_formatter import DataFormatter
from rm_bdd.data_manager import DataManager
from rm_bdd.metadata_manager import MetadataManager

MS_TIMESTAMP = 1_704_067_200_000
SAMPLE_ROW = (
    f"{MS_TIMESTAMP},42000.0,42500.0,41800.0,42200.0,1000.0,"
    f"{MS_TIMESTAMP + 3_600_000},42000000.0,5000,500.0,21000000.0,0"
)

S3_FILENAMES = [
    "data/spot/monthly/klines/BTCUSDT/1m/BTCUSDT-1m-2024-01.zip",
    "data/spot/monthly/klines/BTCUSDT/1m/BTCUSDT-1m-2024-02.zip",
]


# ---------------------------------------------------------------------------
# MetadataManager
# ---------------------------------------------------------------------------

class TestMetadataManagerLogging:
    def test_logs_skip_when_date_already_present(self, tmp_path, caplog):
        mm = MetadataManager(str(tmp_path / "meta.json"))
        mm.update_metadata("BTCUSDT", "1m", "2024-01")

        with caplog.at_level(logging.INFO, logger="rm_bdd.metadata_manager"):
            mm.check_date_not_in_metadata("BTCUSDT", "1m", "2024-01")

        assert any("already exists" in r.message for r in caplog.records)

    def test_no_skip_log_when_date_absent(self, tmp_path, caplog):
        mm = MetadataManager(str(tmp_path / "meta.json"))

        with caplog.at_level(logging.INFO, logger="rm_bdd.metadata_manager"):
            mm.check_date_not_in_metadata("BTCUSDT", "1m", "2024-01")

        assert not any("already exists" in r.message for r in caplog.records)

    def test_logs_skip_for_daily_when_month_present(self, tmp_path, caplog):
        mm = MetadataManager(str(tmp_path / "meta.json"))
        mm.update_metadata("BTCUSDT", "1m", "2024-01")

        with caplog.at_level(logging.INFO, logger="rm_bdd.metadata_manager"):
            mm.check_date_not_in_metadata("BTCUSDT", "1m", "2024-01-15")

        assert any("already exists" in r.message for r in caplog.records)


# ---------------------------------------------------------------------------
# DataDownloader
# ---------------------------------------------------------------------------

class TestDataDownloaderLogging:
    async def test_logs_download_start_and_finish(self, tmp_path, caplog):
        mock_meta = MagicMock()
        mock_meta.check.return_value = True
        downloader = DataDownloader(str(tmp_path) + "/", mock_meta)

        with patch(
            "rm_bdd.data_downloader.get_all_available_filenames_in_daterange",
            new_callable=AsyncMock,
            return_value=S3_FILENAMES,
        ):
            with patch("rm_bdd.data_downloader.download_file", new_callable=AsyncMock, return_value=None):
                with caplog.at_level(logging.INFO, logger="rm_bdd.data_downloader"):
                    await downloader.download("BTCUSDT", "1m")

        messages = [r.message for r in caplog.records]
        assert any("Downloading" in m and "BTCUSDT" in m for m in messages)
        assert any("Finished" in m and "BTCUSDT" in m for m in messages)

    async def test_logs_downloaded_file(self, tmp_path, caplog):
        url_key = "data/spot/monthly/klines/BTCUSDT/1m/BTCUSDT-1m-2024-01.zip"

        with patch("rm_bdd.data_downloader.aiohttp.ClientSession") as mock_cls:
            mock_cls.return_value.__aenter__.side_effect = Exception("network disabled")

            with caplog.at_level(logging.INFO, logger="rm_bdd.data_downloader"):
                result = await download_file(url_key, str(tmp_path) + "/")

        assert result is None
        assert any("Failed" in r.message and "BTCUSDT-1m-2024-01" in r.message for r in caplog.records)


# ---------------------------------------------------------------------------
# DataExtractor
# ---------------------------------------------------------------------------

class TestDataExtractorLogging:
    async def test_logs_extract_start_and_finish(self, tmp_path, caplog):
        download_dir = tmp_path / "downloads"
        extract_dir = tmp_path / "extracts"
        download_dir.mkdir()
        extract_dir.mkdir()

        zip_path = download_dir / "BTCUSDT-1m-2024-01.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("BTCUSDT-1m-2024-01.csv", SAMPLE_ROW)

        mock_meta = MagicMock()
        mock_meta.check.return_value = True
        extractor = DataExtractor(str(download_dir) + "/", str(extract_dir) + "/", mock_meta)

        with caplog.at_level(logging.INFO, logger="rm_bdd.data_extractor"):
            await extractor.extract("BTCUSDT", "1m")

        messages = [r.message for r in caplog.records]
        assert any("Extracting" in m and "BTCUSDT" in m for m in messages)
        assert any("Extracted" in m and "BTCUSDT" in m for m in messages)

    async def test_logs_per_file_at_debug(self, tmp_path, caplog):
        download_dir = tmp_path / "downloads"
        extract_dir = tmp_path / "extracts"
        download_dir.mkdir()
        extract_dir.mkdir()

        zip_path = download_dir / "BTCUSDT-1m-2024-01.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("BTCUSDT-1m-2024-01.csv", SAMPLE_ROW)

        mock_meta = MagicMock()
        mock_meta.check.return_value = True
        extractor = DataExtractor(str(download_dir) + "/", str(extract_dir) + "/", mock_meta)

        with caplog.at_level(logging.DEBUG, logger="rm_bdd.data_extractor"):
            await extractor.extract_files(["BTCUSDT-1m-2024-01.zip"])

        assert any(
            r.levelno == logging.DEBUG and "BTCUSDT-1m-2024-01" in r.message
            for r in caplog.records
        )


# ---------------------------------------------------------------------------
# DataFormatter
# ---------------------------------------------------------------------------

class TestDataFormatterLogging:
    async def test_logs_files_to_format_at_debug(self, tmp_path, caplog):
        extract_dir = tmp_path / "extracts"
        data_dir = tmp_path / "data"
        extract_dir.mkdir()
        data_dir.mkdir()
        (extract_dir / "BTCUSDT-1m-2024-01.csv").write_text(SAMPLE_ROW + "\n")

        mock_meta = MagicMock()
        mock_meta.check.return_value = True
        formatter = DataFormatter(str(extract_dir) + "/", str(data_dir) + "/", mock_meta)

        with patch("rm_bdd.data_formatter.csv_to_partitioned_parquet", new_callable=AsyncMock):
            with caplog.at_level(logging.DEBUG, logger="rm_bdd.data_formatter"):
                await formatter.format_files(["BTCUSDT-1m-2024-01.csv"])

        assert any(
            r.levelno == logging.DEBUG and "Files to format" in r.message
            for r in caplog.records
        )

    async def test_no_debug_log_when_all_skipped(self, tmp_path, caplog):
        """Якщо всі файли вже в метаданих — debug-лог не має з'являтись."""
        extract_dir = tmp_path / "extracts"
        data_dir = tmp_path / "data"
        extract_dir.mkdir()
        data_dir.mkdir()
        (extract_dir / "BTCUSDT-1m-2024-01.csv").write_text(SAMPLE_ROW + "\n")

        mock_meta = MagicMock()
        mock_meta.check.return_value = False  # всі вже оброблені
        formatter = DataFormatter(str(extract_dir) + "/", str(data_dir) + "/", mock_meta)

        with caplog.at_level(logging.DEBUG, logger="rm_bdd.data_formatter"):
            await formatter.format_files(["BTCUSDT-1m-2024-01.csv"])

        assert not any("Files to format" in r.message for r in caplog.records)


# ---------------------------------------------------------------------------
# DataManager
# ---------------------------------------------------------------------------

class TestDataManagerLogging:
    async def test_logs_timing_for_all_stages(self, caplog):
        manager = DataManager(AsyncMock(), AsyncMock(), AsyncMock())

        with caplog.at_level(logging.INFO, logger="rm_bdd.data_manager"):
            await manager.download_and_save("BTCUSDT", "1m")

        messages = [r.message for r in caplog.records]
        assert any("Download stage" in m for m in messages)
        assert any("Extract stage" in m for m in messages)
        assert any("Format stage" in m for m in messages)

    async def test_timing_messages_contain_seconds(self, caplog):
        manager = DataManager(AsyncMock(), AsyncMock(), AsyncMock())

        with caplog.at_level(logging.INFO, logger="rm_bdd.data_manager"):
            await manager.download_and_save("BTCUSDT", "1m")

        timing_messages = [r.message for r in caplog.records if "stage" in r.message.lower()]
        assert len(timing_messages) == 3
        assert all("s" in m for m in timing_messages)
