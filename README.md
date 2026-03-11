# rm-binance-data-downloader

A Python library for downloading, extracting and formatting historical
Binance market data.

The package provides a pipeline that:

1. Downloads data from Binance Vision
2. Extracts compressed archives
3. Formats data into a structured dataset

It is designed for fast data preparation for quantitative trading,
backtesting and data analysis.

------------------------------------------------------------------------

# Installation

``` bash
pip install rm-bdd
```

------------------------------------------------------------------------

# Features

- Download historical Binance data
- Automatic archive extraction
- Data formatting pipeline
- Metadata management
- Async architecture
- Easy integration into trading systems

------------------------------------------------------------------------

# Quick Example

``` python
import asyncio
import time

from rm_bdd import get_manager


async def main():
    downloads_path = "downloads/"
    extracts_path = "extracts/"
    data_path = "data/"
    
    manager = get_manager(downloads_path, extracts_path, data_path)
    await manager.download_and_save("BTCUSDT", "1m")


asyncio.run(main())
```

Read data

``` python
import pandas as pd

df_1m = pd.read_parquet("data", filters=[("symbol", "==", "SOLUSDT"), ("timeframe", "==", "1m")])
```


# Pipeline Overview

The processing pipeline consists of three stages:

### Downloader

Downloads historical data archives from Binance Vision.

### Extractor

Extracts downloaded archives.

### Formatter

Formats extracted CSV data into a structured dataset ready for analysis.

------------------------------------------------------------------------

# Metadata Manager

The library uses a metadata system to track downloaded, extracted and
formatted data.

This prevents duplicate downloads and processing.

------------------------------------------------------------------------

# Example Use Case

Typical workflow:

    download → extract → format → analyze

Used for:

- algorithmic trading
- backtesting
- machine learning datasets
- market research

------------------------------------------------------------------------

# Requirements

Python 3.10+

------------------------------------------------------------------------

# License

MIT
