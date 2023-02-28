import asyncio
import json
import os
from pathlib import Path
from typing import Literal
from zipfile import ZipFile

import aiohttp
from pandas import DataFrame, concat, date_range, read_csv, to_datetime
from typing_extensions import override

from trbox.common.constants import OHLCV_INDEX_NAME
from trbox.common.types import Symbols
from trbox.market import MarketWorker

CACHE_DIR = f'{Path.home()}/.local/share/trbox'

API_BASE = 'https://api.binance.com'
ARCHIVE_BASE = 'https://data.binance.vision/data'

MarketType = Literal[
    'spot',
    # 'futures', # not implemented yet
]
UpdateFreq = Literal[
    'daily',
    # 'monthly', # not implemented yet
]
DataType = Literal[
    # 'aggTrades', # not implemented yet
    'klines',
    # 'trades', # not implemented yet
]
Freq = Literal['1s',
               '1m', '3m', '5m', '15m', '30m',
               '1h', '2h', '4h', '6h', '8h', '12h',
               '1d', ]

RAW_COLUMNS = ['OpenTime', 'Open', 'High', 'Low', 'Close', 'Volume', 'CloseTime',
               'AssetVolume', 'NumberOfTrades', 'TakerBaseAssetVolume', 'TakerQuoteAssetVolume', 'Unused']
SELECTED_COLUMNS = ['Open', 'High', 'Low',
                    'Close', 'Volume', 'CloseTime']


async def fetch_zip(symbol: str,
                    freq: Freq,
                    start: str,
                    end: str,
                    *,
                    market_type: MarketType = 'spot',
                    update_freq: UpdateFreq = 'daily',
                    data_type: DataType = 'klines',):
    async with aiohttp.ClientSession() as session:
        # get file from cache if exists, else download and cache
        async def get_part(date: str):
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
                    with open(cache_url, 'wb') as cache_file:
                        async for chunk in res.content.iter_chunked(1024):
                            cache_file.write(chunk)
                        print(f'written: {cache_url}')
            # open the cache and read as dataframe
            with open(cache_url, 'rb') as cache_file:
                with ZipFile(cache_file).open(f'{cache_name}.csv') as zipped:
                    df = read_csv(zipped, header=None, names=RAW_COLUMNS)
                    df = df[SELECTED_COLUMNS]
                    df = df.rename(columns={'CloseTime': OHLCV_INDEX_NAME})
                    df = df.set_index(OHLCV_INDEX_NAME)
                    df.index = to_datetime(df.index.values*1e6).round('S')
                    df = df.sort_index()
                    return df

        dates = date_range(start, end, freq='D')
        parts = await asyncio.gather(*[get_part(date) for date in dates])
        df = concat(parts, axis=0)
        df = df.sort_index()
        print(df)


async def fetch_api(symbol: str,
                    freq: Freq,
                    start: str,
                    end: str):

    '''
    can only draw max 1000 entries, 
    useless for backtest,
    only useful when fetch some short history data just before live trading to init the startegy
    '''
    path = '/api/v3/klines'
    url = f'{API_BASE}{path}'
    params = dict(symbol=symbol,
                  interval=freq,
                  startTime=int(to_datetime(start).value/1e6),
                  endTime=int(to_datetime(end).value/1e6),)
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as res:
            content = json.loads((await res.content.read()).decode())
            df = DataFrame(content, columns=[
                'OpenTime', 'Open', 'High', 'Low', 'Close', 'Volume', 'CloseTime',
                'AssetVolume', 'NumberOfTrades', 'TakerBaseAssetVolume', 'TakerQuoteAssetVolume', 'Unused'])
            df = df[['Open', 'High', 'Low', 'Close', 'Volume', 'CloseTime']]
            df = df.rename(columns={'CloseTime': 'Date'})
            df['Date'] = to_datetime(df['Date']*1e6).round('S')
            df = df.set_index('Date')
            return df


class BinanceHistoricalWindows(MarketWorker):
    def __init__(self,
                 symbols: Symbols,
                 start: str,
                 end: str,
                 freq: Freq,
                 length: int) -> None:
        super().__init__()
        self._symbols = symbols
        self._start = to_datetime(start)
        self._end = to_datetime(end)
        self._freq = freq
        self._length = length

    @ override
    def working(self) -> None:
        pass


if __name__ == '__main__':
    async def main():
        await fetch_zip('BTCUSDT', '1h', '2023-01-01', '2023-01-10')
    asyncio.run(main())
