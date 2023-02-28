import asyncio
import json
from io import BytesIO
from typing import Literal
from zipfile import ZipFile

import aiohttp
from pandas import DataFrame, concat, read_csv, to_datetime
from typing_extensions import override

from trbox.common.types import Symbols
from trbox.market import MarketWorker

API_BASE = 'https://api.binance.com'
ARCHIVE_BASE = 'https://data.binance.vision/?prefix=data'

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


async def fetch_zip(symbol: str,
                    freq: Freq,
                    start: str,
                    end: str,
                    *,
                    market_type: MarketType = 'spot',
                    update_freq: UpdateFreq = 'daily',
                    data_type: DataType = 'klines',):
    def make_url(date: str) -> str:
        date = str(to_datetime(date).date())
        path = f'{API_BASE}/{market_type}/{update_freq}/{data_type}/{symbol}/{freq}'
        fname = f'{symbol}-{freq}-{date}.zip'
        url = f'{path}/{fname}'
        return url
    url = make_url(start)
    print()
    # params = dict(symbol=symbol,
    #               interval=freq,
    #               startTime=int(to_datetime(start).value/1e6),
    #               endTime=int(to_datetime(end).value/1e6),)
    # async def fetch(url: str,
    #                 session: aiohttp.ClientSession) -> DataFrame:
    #     async with session.get(url) as res:
    #         zipped = ZipFile(BytesIO(await res.content.read()))
    #         csv = zipped.open()
    #         segment = read_csv(csv)
    #         return segment
    #
    # async with aiohttp.ClientSession() as session:
    #     segments: list[DataFrame] = await asyncio.gather(*[fetch(url, session)
    #                                                        for url in urls])
    #     df = concat(segments)
    #     return df


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
