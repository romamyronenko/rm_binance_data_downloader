import os
from functools import partial

import zipfile

from .binance_metadata_manager import BinanceMetadataManager
from .files_parser import _is_filename_in_date_range


class DataExtractor:
    def __init__(self, download_folder, extract_folder, metadata_manager):
        self._download_folder = download_folder
        self._extract_folder = extract_folder
        self._metadata_manager = metadata_manager

    async def extract(self, symbol, timeframe, date_from=None, date_to=None):
        downloaded_files = self._downloaded_files
        files_to_extract = filter(lambda a: a.startswith(f'{symbol.upper()}-{timeframe}'), downloaded_files)
        files_to_extract = list(filter(
            partial(_is_filename_in_date_range, date_from=date_from, date_to=date_to),
            files_to_extract,
        ))
        retval = await self.extract_files(files_to_extract)

        return retval

    async def extract_files(self, filenames):
        filenames = [self._download_folder + filename for filename in filenames]
        filenames = list(
            filter(self._metadata_manager.check, filenames)
        )
        filenames = list(filter(lambda a: a.count("-") == 1 or f'{a.rsplit("-", 1)[0]}.zip' not in filenames, filenames))
        retval = []
        for filename in filenames:
            with zipfile.ZipFile(filename) as zip_file:
                zip_file.extractall(self._extract_folder)
            self._metadata_manager.update(filename)
            retval.append(filename)
        return retval

    @property
    def _downloaded_files(self) -> list[str]:
        return list(filter(lambda a: a.endswith(".zip"), os.listdir(self._download_folder)))


if __name__ == '__main__':
    import asyncio


    async def main():
        extractor = DataExtractor("downloads/", "extracts/", BinanceMetadataManager("extracts/metadata.json"))
        await extractor.extract("BTCUSDT", '1m')


    asyncio.run(main())
