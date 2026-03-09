import json
import logging
import os

logger = logging.getLogger(__name__)


class MetadataManager:
    def __init__(self, file_path):
        self._data = None
        self._file_path = file_path

    def _load_metadata(self):
        if os.path.isfile(self._file_path):
            with open(self._file_path, "r") as f:
                self._data = json.load(f)
        else:
            self._data = {}

    @property
    def data(self):
        if self._data is None:
            self._load_metadata()
        return self._data

    def _save_metadata(self):
        with open(self._file_path, mode="w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)

    def update_metadata(self, symbol: str, timeframe: str, date: str):
        if symbol not in self.data:
            self._data[symbol] = {}

        if timeframe not in self.data[symbol]:
            self._data[symbol][timeframe] = []

        if not self._data[symbol][timeframe] or self._data[symbol][timeframe][-1] != date:
            self._data[symbol][timeframe].append(date)
            self._save_metadata()

    def check_date_not_in_metadata(self, symbol: str, timeframe: str, date: str):
        metadata = self.data.get(symbol, {}).get(timeframe, [])
        date_not_in_metadata = date not in metadata
        date_month_not_in_metadata = date.count("-") != 2 or date.rsplit("-", 1)[0] not in metadata
        result = date_not_in_metadata and date_month_not_in_metadata
        if not result:
            logger.info(f"Data for {symbol} {timeframe} {date} already exists. Skip.")
        return result
