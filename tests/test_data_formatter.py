from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from rm_bdd.data_formatter import DataFormatter

MS_TIMESTAMP = 1_704_067_200_000
SAMPLE_ROW = (
    f"{MS_TIMESTAMP},42000.0,42500.0,41800.0,42200.0,1000.0,"
    f"{MS_TIMESTAMP + 3_600_000},42000000.0,5000,500.0,21000000.0,0"
)


@pytest.fixture
def dirs(tmp_path):
    extract_dir = tmp_path / "extracts"
    data_dir = tmp_path / "data"
    extract_dir.mkdir()
    data_dir.mkdir()
    return extract_dir, data_dir


def make_formatter(dirs, meta_check=True):
    extract_dir, data_dir = dirs
    mock_meta = MagicMock()
    mock_meta.check.return_value = meta_check
    return (
        DataFormatter(str(extract_dir) + "/", str(data_dir) + "/", mock_meta),
        extract_dir,
        data_dir,
        mock_meta,
    )


class TestFormatFiles:
    async def test_returns_empty_for_empty_input(self, dirs):
        formatter, _, _, _ = make_formatter(dirs)
        result = await formatter.format_files([])
        assert result == []

    async def test_skips_if_in_metadata(self, dirs):
        extract_dir, _ = dirs
        csv = extract_dir / "BTCUSDT-1m-2024-01.csv"
        csv.write_text(SAMPLE_ROW + "\n")
        formatter, _, _, mock_meta = make_formatter(dirs, meta_check=False)

        result = await formatter.format_files(["BTCUSDT-1m-2024-01.csv"])

        assert result == []
        mock_meta.update.assert_not_called()

    async def test_calls_parquet_conversion(self, dirs):
        extract_dir, _ = dirs
        csv = extract_dir / "BTCUSDT-1m-2024-01.csv"
        csv.write_text(SAMPLE_ROW + "\n")
        formatter, _, _, mock_meta = make_formatter(dirs)

        with patch("rm_bdd.data_formatter.csv_to_partitioned_parquet", new_callable=AsyncMock) as mock_pq:
            result = await formatter.format_files(["BTCUSDT-1m-2024-01.csv"])

        mock_pq.assert_called_once()
        mock_meta.update.assert_called_once()
        assert len(result) == 1

    async def test_updates_metadata_after_format(self, dirs):
        extract_dir, _ = dirs
        csv = extract_dir / "BTCUSDT-1m-2024-01.csv"
        csv.write_text(SAMPLE_ROW + "\n")
        formatter, _, _, mock_meta = make_formatter(dirs)

        with patch("rm_bdd.data_formatter.csv_to_partitioned_parquet", new_callable=AsyncMock):
            await formatter.format_files(["BTCUSDT-1m-2024-01.csv"])

        mock_meta.update.assert_called_once()


class TestFormat:
    async def test_filters_by_symbol(self, dirs):
        extract_dir, _ = dirs
        for symbol in ("BTCUSDT", "ETHUSDT"):
            (extract_dir / f"{symbol}-1m-2024-01.csv").write_text(SAMPLE_ROW + "\n")
        formatter, _, _, _ = make_formatter(dirs)

        with patch("rm_bdd.data_formatter.csv_to_partitioned_parquet", new_callable=AsyncMock) as mock_pq:
            await formatter.format("BTCUSDT", "1m")

        args = mock_pq.call_args[0][0]
        assert all("BTCUSDT" in f for f in args)

    async def test_filters_by_date_range(self, dirs):
        extract_dir, _ = dirs
        for month in ("01", "02", "03"):
            (extract_dir / f"BTCUSDT-1m-2024-{month}.csv").write_text(SAMPLE_ROW + "\n")
        formatter, _, _, _ = make_formatter(dirs)

        with patch("rm_bdd.data_formatter.csv_to_partitioned_parquet", new_callable=AsyncMock) as mock_pq:
            await formatter.format("BTCUSDT", "1m", date_from="2024-02", date_to="2024-02")

        args = mock_pq.call_args[0][0]
        assert len(args) == 1
        assert "2024-02" in args[0]
