from .metadata_manager import MetadataManager


def _get_data_from_filename(filename) -> tuple[str, str, str]:
    filename = filename.split(".", 1)[0]
    symbol, timeframe, date = filename.split("-", 2)
    return symbol, timeframe, date


class BinanceMetadataManager:
    def __init__(self, file_path):
        self._metadata_manager = MetadataManager(file_path)

    def update(self, filename):
        symbol, timeframe, date = _get_data_from_filename(filename.rsplit("/", 1)[1])
        self._metadata_manager.update_metadata(symbol, timeframe, date)

    def check(self, filename):
        symbol, timeframe, date = _get_data_from_filename(filename.rsplit("/", 1)[1])

        return self._metadata_manager.check_date_not_in_metadata(
            symbol, timeframe, date
        )
