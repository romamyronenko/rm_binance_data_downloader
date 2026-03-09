import time


class DataManager:
    def __init__(self, downloader, extractor, formatter):
        self._downloader = downloader
        self._extractor = extractor
        self._formatter = formatter

    async def download_and_save(self, symbol, timeframe, date_from=None, date_to=None):
        start = time.time()
        await self._downloader.download(symbol, timeframe, date_from=date_from, date_to=date_to)
        print("download time: ", time.time() - start)

        start = time.time()
        await self._extractor.extract(symbol, timeframe, date_from=date_from, date_to=date_to)
        print("extract time: ", time.time() - start)

        start = time.time()
        await self._formatter.format(symbol, timeframe, date_from=date_from, date_to=date_to)
        print("format time: ", time.time() - start)


if __name__ == '__main__':
    import asyncio
    from rm_binance_data_downloader.src.data_downloader import DataDownloader
    from rm_binance_data_downloader.src.data_extractor import DataExtractor
    from rm_binance_data_downloader.src.data_formatter import DataFormatter
    from rm_binance_data_downloader.src.binance_metadata_manager import BinanceMetadataManager

    downloader = DataDownloader("downloads/", BinanceMetadataManager("downloads/metadata.json"))
    extractor = DataExtractor("downloads/", "extracts/", BinanceMetadataManager("extracts/metadata.json"))
    formatter = DataFormatter("extracts/", "data/", BinanceMetadataManager("data/metadata.json"))

    manager = DataManager(downloader, extractor, formatter)


    async def main():
        await manager.download_and_save("BTCUSDT", '1m')


    start = time.time()
    asyncio.run(main())

    print(time.time() - start)
