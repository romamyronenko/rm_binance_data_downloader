import pandas as pd
import pytest

from rm_bdd.csvs_to_parquet import csv_to_partitioned_parquet, normalize_time

# Реальний ms-timestamp: 2024-01-01 00:00:00 UTC
MS_TIMESTAMP = 1_704_067_200_000
NS_TIMESTAMP = MS_TIMESTAMP * 1000  # > 10^13 → наносекунди

SAMPLE_ROW = (
    f"{MS_TIMESTAMP},42000.0,42500.0,41800.0,42200.0,1000.0,"
    f"{MS_TIMESTAMP + 3_600_000},42000000.0,5000,500.0,21000000.0,0"
)


class TestNormalizeTime:
    def test_milliseconds_unchanged(self):
        series = pd.Series([MS_TIMESTAMP])
        result = normalize_time(series.copy())
        assert result.iloc[0] == MS_TIMESTAMP

    def test_nanoseconds_converted_to_ms(self):
        series = pd.Series([NS_TIMESTAMP])
        result = normalize_time(series.copy())
        assert result.iloc[0] == MS_TIMESTAMP

    def test_mixed_values(self):
        series = pd.Series([MS_TIMESTAMP, NS_TIMESTAMP])
        result = normalize_time(series.copy())
        assert result.iloc[0] == MS_TIMESTAMP
        assert result.iloc[1] == MS_TIMESTAMP

    def test_empty_series(self):
        series = pd.Series([], dtype="int64")
        result = normalize_time(series.copy())
        assert len(result) == 0


class TestCsvToPartitionedParquet:
    async def test_creates_parquet_output(self, tmp_path):
        csv_file = tmp_path / "BTCUSDT-1m-2024-01-01.csv"
        csv_file.write_text(SAMPLE_ROW + "\n")
        output_dir = tmp_path / "data"
        output_dir.mkdir()

        await csv_to_partitioned_parquet([str(csv_file)], "BTCUSDT", "1m", str(output_dir))

        df = pd.read_parquet(str(output_dir), filters=[("symbol", "==", "BTCUSDT")])
        assert len(df) == 1

    async def test_adds_symbol_and_timeframe_columns(self, tmp_path):
        csv_file = tmp_path / "BTCUSDT-1m-2024-01-01.csv"
        csv_file.write_text(SAMPLE_ROW + "\n")
        output_dir = tmp_path / "data"
        output_dir.mkdir()

        await csv_to_partitioned_parquet([str(csv_file)], "BTCUSDT", "1m", str(output_dir))

        df = pd.read_parquet(str(output_dir))
        assert df["symbol"].iloc[0] == "BTCUSDT"
        assert df["timeframe"].iloc[0] == "1m"

    async def test_adds_date_partition_columns(self, tmp_path):
        csv_file = tmp_path / "BTCUSDT-1m-2024-01-01.csv"
        csv_file.write_text(SAMPLE_ROW + "\n")
        output_dir = tmp_path / "data"
        output_dir.mkdir()

        await csv_to_partitioned_parquet([str(csv_file)], "BTCUSDT", "1m", str(output_dir))

        df = pd.read_parquet(str(output_dir))
        assert df["year"].iloc[0] == 2024
        assert df["month"].iloc[0] == 1
        assert df["day"].iloc[0] == 1

    async def test_concatenates_multiple_files(self, tmp_path):
        for day in ("01", "02"):
            csv_file = tmp_path / f"BTCUSDT-1m-2024-01-{day}.csv"
            csv_file.write_text(SAMPLE_ROW + "\n")
        output_dir = tmp_path / "data"
        output_dir.mkdir()

        files = [str(tmp_path / f"BTCUSDT-1m-2024-01-{d}.csv") for d in ("01", "02")]
        await csv_to_partitioned_parquet(files, "BTCUSDT", "1m", str(output_dir))

        df = pd.read_parquet(str(output_dir))
        assert len(df) == 2
