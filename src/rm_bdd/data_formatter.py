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
        filenames = [os.path.join(self._extract_folder, f) for f in filenames]
        # skip daily files when the corresponding monthly file is already present
        filenames = [f for f in filenames if f'{f.rsplit("-", 1)[0]}.csv' not in filenames]

        if not filenames:
            return []

        symbol = os.path.basename(filenames[0]).split("-", 1)[0]
        timeframe = os.path.basename(filenames[0]).split("-", 2)[1]
        filenames = list(filter(self._metadata_manager.check, filenames))

        if filenames:
            logger.debug(f"Files to format: {filenames}")
            await csv_to_partitioned_parquet(filenames, symbol, timeframe, self._data_folder)

            for filename in filenames:
                self._metadata_manager.update(filename)

        return filenames

    @property
    def _extracted_files(self) -> list[str]:
        if not os.path.isdir(self._extract_folder):
            return []
        return [f for f in os.listdir(self._extract_folder) if f.endswith(".csv")]


if __name__ == '__main__':
    import asyncio
    from .binance_metadata_manager import BinanceMetadataManager

    async def main():
        formatter = DataFormatter("extracts/", "data/", BinanceMetadataManager("data/metadata.json"))
        await formatter.format("BTCUSDT", '1m')

    asyncio.run(main())
