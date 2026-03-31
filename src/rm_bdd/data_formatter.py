import logging
import os
from functools import partial

from .csvs_to_parquet import csv_to_partitioned_parquet
from .files_parser import _is_filename_in_date_range

logger = logging.getLogger(__name__)


class DataFormatter:
    def __init__(self, extract_folder, data_folder, metadata_manager):
        self._extract_folder = extract_folder
        self._data_folder = data_folder
        self._metadata_manager = metadata_manager

    async def format(self, symbol, timeframe, date_from=None, date_to=None):
        extracted_files = self._extracted_files
        files_to_format = filter(lambda a: a.startswith(f'{symbol.upper()}-{timeframe}'), extracted_files)
        files_to_format = list(filter(
            partial(_is_filename_in_date_range, date_from=date_from, date_to=date_to),
            files_to_format,
        ))

        await self.format_files(files_to_format)

    async def format_files(self, filenames):
        os.makedirs(self._data_folder, exist_ok=True)
        filenames = [self._extract_folder + filename for filename in filenames]

        filenames = list(
            filter(lambda a: a.count("-") == 1 or f'{a.rsplit("-", 1)[0]}.csv' not in filenames, filenames))

        if not filenames:
            return []

        retval = []
        symbol = filenames[0].rsplit("/", 1)[-1].split("-", 1)[0]
        timeframe = filenames[0].rsplit("/", 1)[-1].split("-", 2)[1]
        filenames = list(
            filter(self._metadata_manager.check, filenames)
        )
        if filenames:
            logger.debug(f"Files to format: {filenames}")
            await csv_to_partitioned_parquet(filenames, symbol, timeframe, self._data_folder)

            for filename in filenames:
                self._metadata_manager.update(filename)
                retval.append(filename)
        return retval

    @property
    def _extracted_files(self) -> list[str]:
        return list(filter(lambda a: a.endswith(".csv"), os.listdir(self._extract_folder)))


if __name__ == '__main__':
    def main():
        from .binance_metadata_manager import BinanceMetadataManager
        formatter = DataFormatter("extracts/", "data/", BinanceMetadataManager("data/metadata.json"))
        formatter.format("BTCUSDT", '1m')


    main()
