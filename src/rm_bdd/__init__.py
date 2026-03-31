import os

from . import data_downloader, data_formatter, data_manager, binance_metadata_manager
from . import data_extractor


def get_manager(download_folder="downloads/", extract_folder="extracts/", data_folder="data"):
    downloader = data_downloader.DataDownloader(
        download_folder,
        binance_metadata_manager.BinanceMetadataManager(os.path.join(download_folder, "metadata.json")),
    )
    extractor = data_extractor.DataExtractor(
        download_folder,
        extract_folder,
        binance_metadata_manager.BinanceMetadataManager(os.path.join(extract_folder, "metadata.json")),
    )
    formatter = data_formatter.DataFormatter(
        extract_folder,
        data_folder,
        binance_metadata_manager.BinanceMetadataManager(os.path.join(data_folder, "metadata.json")),
    )
    return data_manager.DataManager(downloader, extractor, formatter)
