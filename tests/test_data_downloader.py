from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from rm_bdd.data_downloader import DataDownloader

S3_FILENAMES = [
    "data/spot/monthly/klines/BTCUSDT/1m/BTCUSDT-1m-2024-01.zip",
    "data/spot/monthly/klines/BTCUSDT/1m/BTCUSDT-1m-2024-02.zip",
]


@pytest.fixture
def mock_meta():
    m = MagicMock()
    m.check.return_value = True
    return m


class TestDataDownloader:
    async def test_download_calls_gather_for_each_file(self, tmp_path, mock_meta):
        downloader = DataDownloader(str(tmp_path) + "/", mock_meta)

        with patch(
            "rm_bdd.data_downloader.get_all_available_filenames_in_daterange",
            new_callable=AsyncMock,
            return_value=S3_FILENAMES,
        ):
            with patch(
                "rm_bdd.data_downloader.download_file",
                new_callable=AsyncMock,
            ) as mock_dl:
                mock_dl.side_effect = [
                    str(tmp_path / "BTCUSDT-1m-2024-01.zip"),
                    str(tmp_path / "BTCUSDT-1m-2024-02.zip"),
                ]
                await downloader.download("BTCUSDT", "1m")

        assert mock_dl.call_count == 2

    async def test_download_skips_files_in_metadata(self, tmp_path, mock_meta):
        mock_meta.check.side_effect = lambda f: "2024-02" in f

        downloader = DataDownloader(str(tmp_path) + "/", mock_meta)

        with patch(
            "rm_bdd.data_downloader.get_all_available_filenames_in_daterange",
            new_callable=AsyncMock,
            return_value=S3_FILENAMES,
        ):
            with patch(
                "rm_bdd.data_downloader.download_file",
                new_callable=AsyncMock,
                return_value=str(tmp_path / "BTCUSDT-1m-2024-02.zip"),
            ) as mock_dl:
                await downloader.download("BTCUSDT", "1m")

        assert mock_dl.call_count == 1
        call_args = mock_dl.call_args[0][0]
        assert "2024-02" in call_args

    async def test_download_updates_metadata_for_each_result(self, tmp_path, mock_meta):
        downloader = DataDownloader(str(tmp_path) + "/", mock_meta)

        with patch(
            "rm_bdd.data_downloader.get_all_available_filenames_in_daterange",
            new_callable=AsyncMock,
            return_value=S3_FILENAMES,
        ):
            with patch(
                "rm_bdd.data_downloader.download_file",
                new_callable=AsyncMock,
                side_effect=[
                    str(tmp_path / "BTCUSDT-1m-2024-01.zip"),
                    str(tmp_path / "BTCUSDT-1m-2024-02.zip"),
                ],
            ):
                await downloader.download("BTCUSDT", "1m")

        assert mock_meta.update.call_count == 2

    async def test_download_returns_results(self, tmp_path, mock_meta):
        downloader = DataDownloader(str(tmp_path) + "/", mock_meta)

        with patch(
            "rm_bdd.data_downloader.get_all_available_filenames_in_daterange",
            new_callable=AsyncMock,
            return_value=S3_FILENAMES,
        ):
            with patch(
                "rm_bdd.data_downloader.download_file",
                new_callable=AsyncMock,
                side_effect=[
                    str(tmp_path / "BTCUSDT-1m-2024-01.zip"),
                    str(tmp_path / "BTCUSDT-1m-2024-02.zip"),
                ],
            ):
                results = await downloader.download("BTCUSDT", "1m")

        assert len(results) == 2

    async def test_download_passes_date_range_to_filenames_fn(self, tmp_path, mock_meta):
        downloader = DataDownloader(str(tmp_path) + "/", mock_meta)

        with patch(
            "rm_bdd.data_downloader.get_all_available_filenames_in_daterange",
            new_callable=AsyncMock,
            return_value=[],
        ) as mock_fn:
            await downloader.download("BTCUSDT", "1m", date_from="2024-01", date_to="2024-03")

        mock_fn.assert_called_once_with("BTCUSDT", "1m", "2024-01", "2024-03")
