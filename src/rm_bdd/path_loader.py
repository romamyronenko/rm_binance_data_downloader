import asyncio

import aiohttp
import xmltodict

URL_TEMPLATE = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
SEMAPHORE = asyncio.Semaphore(300)


async def get_all_paths(prefix: str, delimiter="/"):
    responses = await get_all_path_responses(prefix, delimiter)
    retval = []
    for response in responses:
        common_prefixes = response.get("ListBucketResult", {}).get("CommonPrefixes", [])
        if isinstance(common_prefixes, list):
            retval.extend([i["Prefix"] for i in common_prefixes])
        else:
            retval.append(common_prefixes["Prefix"])
    return retval


async def get_all_path_responses(prefix: str, delimiter="/", marker=None, **params):
    is_truncated = True
    responses = []
    while is_truncated:
        response = await get_paths_response_json(prefix, delimiter, marker, **params)
        is_truncated = (
            response.get("ListBucketResult", {}).get("IsTruncated", "false") == "true"
        )
        responses.append(response)
        marker = response.get("ListBucketResult", {}).get("NextMarker", None)

    return responses


async def get_paths_response_json(prefix: str, delimiter="/", marker=None, **params):
    if not prefix.endswith("/"):
        prefix += "/"
    params = {"prefix": prefix, "delimiter": delimiter, "marker": marker, **params}
    params = {k: v for k, v in params.items() if v is not None}
    if prefix.endswith("/"):
        prefix = prefix[:-1]
    url = URL_TEMPLATE.format(prefix=prefix)
    async with SEMAPHORE:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                text = await response.text()
                return xmltodict.parse(text)


if __name__ == "__main__":

    async def main():
        responses = await get_all_path_responses("data/spot/monthly/klines/SOLUSDT/1m")
        print(
            [
                i.get("Key")
                for response in responses for i in response.get("ListBucketResult", {}).get("Contents", [])
            ]
        )

    asyncio.run(main())
