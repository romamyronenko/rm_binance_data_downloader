import asyncio
import datetime
import re
from functools import partial

from .binance_metadata_manager import _get_data_from_filename
from .path_loader import get_all_path_responses

DAY_DATE_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}$")
async def _get_all_available_filenames(symbol, timeframe) -> list[str]:
    # get all monthly data
    # get all daily data for last month
    path = f"data/spot/monthly/klines/{symbol}/{timeframe}"
    monthly = await get_all_path_responses(f"data/spot/monthly/klines/{symbol}/{timeframe}")

    filenames = [item['Key'] for item in monthly[0]['ListBucketResult'].get('Contents', [])]
    file_path, year, month = filenames[-1].rsplit(".", 2)[0].rsplit("-", 2)

    file_path = file_path.replace("monthly", "daily")
    if month == '12':
        year = "%02i"%(int(year) + 1)
    else:
        month = "%02i"%(int(month) + 1)

    file_path = "-".join([file_path, year, month])

    path = path.replace("monthly", "daily")

    daily = await get_all_path_responses(path, marker=file_path)

    filenames.extend([item['Key'] for item in daily[0]['ListBucketResult'].get('Contents', [])])
    return filenames


def str_to_datetime(date: str) -> datetime.datetime:
    if DAY_DATE_REGEX.match(date):
        return datetime.datetime.strptime(date, "%Y-%m-%d")
    return datetime.datetime.strptime(date, "%Y-%m")


def _is_filename_in_date_range(filename: str, date_from: str, date_to: str) -> bool:
    *_, date = _get_data_from_filename(filename)
    date = str_to_datetime(date)
    retval = True
    if date_from:
        date_from = str_to_datetime(date_from)
        retval = retval and date >= date_from

    if date_to:
        date_to = str_to_datetime(date_to)
        retval =  retval and date <= date_to
    return retval


async def get_all_available_filenames_in_daterange(
        symbol, timeframe, date_from=None, date_to=None
) -> list[str]:
    filenames = await _get_all_available_filenames(symbol, timeframe)
    if date_from or date_to:
        filenames = list(filter(
            partial(_is_filename_in_date_range, date_from=date_from, date_to=date_to),
            filenames,
        ))
    return filenames


if __name__ == '__main__':
    async def main():
        # await _get_all_available_filenames("BTCUSDT", timeframe="1m")
        # result = await get_all_available_filenames_in_daterange("BTCUSDT", '1m', '2024-03', '2024-05')
        # result = await get_all_available_filenames_in_daterange("BTCUSDT", '1m')
        result = await get_all_available_filenames_in_daterange("BTCUSDT", '1m', date_from="2025-09")
        print(result)
        ...

    asyncio.run(main())
