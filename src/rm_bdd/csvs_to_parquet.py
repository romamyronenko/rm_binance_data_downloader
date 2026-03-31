import pandas as pd


def normalize_time(series):
    """
    Визначає, чи open_time у мілісекундах чи наносекундах,
    і нормалізує до мілісекунд.
    """
    series[series > 10 ** 13] = series[series > 10 ** 13] // 1000
    return series


async def csv_to_partitioned_parquet(files, symbol, timeframe, path="data"):
    columns = [
        "open_time",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "close_time",
        "quote_asset_volume",
        "number_of_trades",
        "taker_buy_base_asset_volume",
        "taker_buy_quote_asset_volume",
        "ignore",
    ]
    df = pd.concat(
        [pd.read_csv(file, names=columns) for file in files], ignore_index=True
    )
    df["open_time"] = normalize_time(df["open_time"])
    df["close_time"] = normalize_time(df["close_time"])
    df["year"] = pd.to_datetime(df["open_time"], unit="ms", utc=True).dt.year
    df["month"] = pd.to_datetime(df["open_time"], unit="ms", utc=True).dt.month
    df["day"] = pd.to_datetime(df["open_time"], unit="ms", utc=True).dt.day
    df["symbol"] = symbol
    df["timeframe"] = timeframe
    df.to_parquet(path, partition_cols=["symbol", "timeframe", "year", "month", "day"], max_partitions=5000)
