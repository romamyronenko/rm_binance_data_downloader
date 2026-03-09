# rm-binance-data-downloader

A Python library for downloading, extracting and formatting historical
Binance market data.

The package provides a pipeline that:

1.  Downloads data from Binance Vision
2.  Extracts compressed archives
3.  Formats data into a structured dataset

It is designed for fast data preparation for quantitative trading,
backtesting and data analysis.

------------------------------------------------------------------------

# Installation

``` bash
pip install rm-bdd
```

------------------------------------------------------------------------

# Features

-   Download historical Binance data
-   Automatic archive extraction
-   Data formatting pipeline
-   Metadata management
-   Async architecture
-   Easy integration into trading systems

------------------------------------------------------------------------

# Quick Example

``` python
import asyncio
import time

from rm_bdd.data_downloader import DataDownloader
from rm_bdd.data_extractor import DataExtractor
from rm_bdd.data_formatter import DataFormatter
from rm_bdd.binance_metadata_manager import BinanceMetadataManager


class DataManager:

    def __init__(self, downloader, extractor, formatter):
        self._downloader = downloader
        self._extractor = extractor
        self._formatter = formatter

    async def download_and_save(self, symbol, timeframe, date_from=None, date_to=None):

        start = time.time()
        await self._downloader.download(symbol, timeframe, date_from=date_from, date_to=date_to)
        print("download time:", time.time() - start)

        start = time.time()
        await self._extractor.extract(symbol, timeframe, date_from=date_from, date_to=date_to)
        print("extract time:", time.time() - start)

        start = time.time()
        await self._formatter.format(symbol, timeframe, date_from=date_from, date_to=date_to)
        print("format time:", time.time() - start)


async def main():

    downloader = DataDownloader(
        "downloads/",
        BinanceMetadataManager("downloads/metadata.json")
    )

    extractor = DataExtractor(
        "downloads/",
        "extracts/",
        BinanceMetadataManager("extracts/metadata.json")
    )

    formatter = DataFormatter(
        "extracts/",
        "data/",
        BinanceMetadataManager("data/metadata.json")
    )

    manager = DataManager(downloader, extractor, formatter)

    await manager.download_and_save("BTCUSDT", "1m")


asyncio.run(main())
```

------------------------------------------------------------------------

# Result Folder Structure

After execution the folders will look like:

    downloads/
        BTCUSDT/
        metadata.json

    extracts/
        BTCUSDT/
        metadata.json

    data/
        BTCUSDT/
        metadata.json

------------------------------------------------------------------------

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

-   algorithmic trading
-   backtesting
-   machine learning datasets
-   market research

------------------------------------------------------------------------

# Requirements

Python 3.10+

------------------------------------------------------------------------

# License

MIT
