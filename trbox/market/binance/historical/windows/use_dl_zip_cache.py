import asyncio
# import io
import os
from pathlib import Path
from zipfile import ZipFile

# import aiofiles
import aiohttp
from pandas import DataFrame, concat, date_range, read_csv, to_datetime

from trbox.common.constants import OHLCV_INDEX_NAME
from trbox.market.binance.historical.windows.constants import (
    ARCHIVE_BASE, CACHE_DIR, RAW_COLUMNS, SELECTED_COLUMNS, DataType, Freq,
    MarketType, UpdateFreq)


async def fetch_zip(symbol: str,
                    freq: Freq,
                    start: str,
                    end: str,
                    *,
                    market_type: MarketType = 'spot',
                    update_freq: UpdateFreq = 'daily',
                    data_type: DataType = 'klines',) -> DataFrame:
    async with aiohttp.ClientSession() as session:
        # get file from cache if exists, else download and cache
        async def get_part(date: str) -> DataFrame:
            date = str(to_datetime(date).date())
            cache_dir = f'{CACHE_DIR}/{market_type}/{update_freq}/{data_type}/{symbol}/{freq}'
            cache_name = f'{symbol}-{freq}-{date}'
            cache_url = f'{cache_dir}/{cache_name}.zip'
            # check if file exist in cache, if not, download first
            if not os.path.isfile(cache_url):
                download_path = f'{ARCHIVE_BASE}/{market_type}/{update_freq}/{data_type}/{symbol}/{freq}'
                download_fname = f'{symbol}-{freq}-{date}.zip'
                download_url = f'{download_path}/{download_fname}'
                async with session.get(download_url) as res:
                    assert res.status == 200
                    print(f'downloaded: {download_url}')
                    Path(cache_dir).mkdir(parents=True, exist_ok=True)
                    # async with aiofiles.open(cache_url, 'wb') as cache_file:
                    with open(cache_url, 'wb') as cache_file:
                        async for chunk in res.content.iter_chunked(1024):
                            # await cache_file.write(chunk)
                            cache_file.write(chunk)
                        print(f'written: {cache_url}')
            # open the cache and read as dataframe
            # async with aiofiles.open(cache_url, 'rb') as cache_file:
            with open(cache_url, 'rb') as cache_file:
                # with ZipFile(io.BytesIO(await cache_file.read())).open(f'{cache_name}.csv') as zipped:
                with ZipFile(cache_file).open(f'{cache_name}.csv') as zipped:
                    df = read_csv(zipped, header=None, names=RAW_COLUMNS)
                    df = df[SELECTED_COLUMNS]
                    df = df.rename(columns={'CloseTime': OHLCV_INDEX_NAME})
                    df = df.set_index(OHLCV_INDEX_NAME)
                    df.index = to_datetime(df.index.values*1e6).round('S')
                    df = df.sort_index()
                    return df

        dates = date_range(start, end, freq='D')
        parts: list[DataFrame] = await asyncio.gather(*[get_part(date) for date in dates])
        df = concat(parts, axis=0)
        df = df.sort_index()
        return df
