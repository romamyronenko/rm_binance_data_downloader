import asyncio
import logging
import os

import aiohttp

from .files_parser import get_all_available_filenames_in_daterange

logger = logging.getLogger(__name__)
BASE_VISION_URL = "https://data.binance.vision/"


async def download_file(key, folder, session: aiohttp.ClientSession) -> str | None:
    logger.info(f"Downloading {key} to {folder}")
    url = BASE_VISION_URL + key

    os.makedirs(folder, exist_ok=True)
    try:
        local_filename = os.path.join(folder, url.split("/")[-1])
        async with session.get(url) as r:
            r.raise_for_status()
            with open(local_filename, "wb") as f:
                async for chunk in r.content.iter_chunked(8192):
                    chunk: bytes
                    f.write(chunk)
        logger.info(f"Downloaded {key} to {local_filename}")
        return str(local_filename)
    except Exception as e:
        logger.error(f"Failed to download {key}: {e}")
        return None


class DataDownloader:
    def __init__(self, download_folder, metadata_manager):
        self._download_folder = download_folder
        self._metadata_manager = metadata_manager

    async def download(self, symbol, timeframe, date_from=None, date_to=None):
        filenames = await get_all_available_filenames_in_daterange(
            symbol, timeframe, date_from, date_to
        )

        filenames = list(filter(self._metadata_manager.check, filenames))

        logger.info(
            f"Downloading {timeframe} data for {symbol} from {date_from} to {date_to}"
        )

        async with aiohttp.ClientSession() as session:
            results = await asyncio.gather(
                *(download_file(filename, self._download_folder, session) for filename in filenames)
            )

        logger.info(f"Finished downloading {timeframe} data for {symbol}")
        logger.debug(f"Downloaded {len(results)} results for {symbol}")

        for filename in results:
            if filename is not None:
                self._metadata_manager.update(filename)

        return results


if __name__ == '__main__':
    from .binance_metadata_manager import BinanceMetadataManager

    async def main():
        downloader = DataDownloader("downloads/", BinanceMetadataManager("downloads/metadata.json"))
        await downloader.download("BTCUSDT", '1m')

    asyncio.run(main())
