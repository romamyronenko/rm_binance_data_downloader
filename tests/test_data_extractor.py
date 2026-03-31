import zipfile
from unittest.mock import MagicMock

import pytest

from rm_bdd.data_extractor import DataExtractor


def make_zip(path, inner_name, content="data"):
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr(inner_name, content)


@pytest.fixture
def dirs(tmp_path):
    download_dir = tmp_path / "downloads"
    extract_dir = tmp_path / "extracts"
    download_dir.mkdir()
    extract_dir.mkdir()
    return download_dir, extract_dir


def make_extractor(dirs, meta_check=True):
    download_dir, extract_dir = dirs
    mock_meta = MagicMock()
    mock_meta.check.return_value = meta_check
    return (
        DataExtractor(str(download_dir) + "/", str(extract_dir) + "/", mock_meta),
        download_dir,
        extract_dir,
        mock_meta,
    )


class TestExtractFiles:
    async def test_extracts_zip_to_folder(self, dirs):
        download_dir, extract_dir = dirs
        make_zip(str(download_dir / "BTCUSDT-1m-2024-01.zip"), "BTCUSDT-1m-2024-01.csv")
        extractor, _, _, mock_meta = make_extractor(dirs)

        result = await extractor.extract_files(["BTCUSDT-1m-2024-01.zip"])

        assert (extract_dir / "BTCUSDT-1m-2024-01.csv").exists()
        assert len(result) == 1
        mock_meta.update.assert_called_once()

    async def test_skips_file_if_in_metadata(self, dirs):
        download_dir, extract_dir = dirs
        make_zip(str(download_dir / "BTCUSDT-1m-2024-01.zip"), "BTCUSDT-1m-2024-01.csv")
        extractor, _, _, mock_meta = make_extractor(dirs, meta_check=False)

        result = await extractor.extract_files(["BTCUSDT-1m-2024-01.zip"])

        assert result == []
        assert not (extract_dir / "BTCUSDT-1m-2024-01.csv").exists()
        mock_meta.update.assert_not_called()

    async def test_returns_empty_for_empty_input(self, dirs):
        extractor, _, _, _ = make_extractor(dirs)
        result = await extractor.extract_files([])
        assert result == []

    async def test_updates_metadata_after_extract(self, dirs):
        download_dir, _ = dirs
        make_zip(str(download_dir / "BTCUSDT-1m-2024-01.zip"), "BTCUSDT-1m-2024-01.csv")
        extractor, _, _, mock_meta = make_extractor(dirs)

        await extractor.extract_files(["BTCUSDT-1m-2024-01.zip"])

        mock_meta.update.assert_called_once()


class TestExtract:
    async def test_filters_by_symbol(self, dirs):
        download_dir, _ = dirs
        make_zip(str(download_dir / "BTCUSDT-1m-2024-01.zip"), "BTCUSDT-1m-2024-01.csv")
        make_zip(str(download_dir / "ETHUSDT-1m-2024-01.zip"), "ETHUSDT-1m-2024-01.csv")
        extractor, _, _, _ = make_extractor(dirs)

        result = await extractor.extract("BTCUSDT", "1m")

        assert len(result) == 1
        assert "BTCUSDT" in result[0]

    async def test_filters_by_timeframe(self, dirs):
        download_dir, _ = dirs
        make_zip(str(download_dir / "BTCUSDT-1m-2024-01.zip"), "BTCUSDT-1m-2024-01.csv")
        make_zip(str(download_dir / "BTCUSDT-4h-2024-01.zip"), "BTCUSDT-4h-2024-01.csv")
        extractor, _, _, _ = make_extractor(dirs)

        result = await extractor.extract("BTCUSDT", "1m")

        assert len(result) == 1
        assert "1m" in result[0]

    async def test_filters_by_date_range(self, dirs):
        download_dir, _ = dirs
        for month in ("01", "02", "03"):
            make_zip(
                str(download_dir / f"BTCUSDT-1m-2024-{month}.zip"),
                f"BTCUSDT-1m-2024-{month}.csv",
            )
        extractor, _, _, _ = make_extractor(dirs)

        result = await extractor.extract("BTCUSDT", "1m", date_from="2024-02", date_to="2024-02")

        assert len(result) == 1
        assert "2024-02" in result[0]
