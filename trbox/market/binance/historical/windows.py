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

BASE_ENDPOINT = 'https://api.binance.com'

Freq = Literal['1s',
               '1m', '3m', '5m', '15m', '30m',
               '1h', '2h', '4h', '6h', '8h', '12h',
               '1d', ]


async def fetch_zip(urls: list[str]) -> DataFrame:
    async def fetch(url: str,
                    session: aiohttp.ClientSession) -> DataFrame:
        async with session.get(url) as res:
            zipped = ZipFile(BytesIO(await res.content.read()))
            csv = zipped.open()
            segment = read_csv(csv)
            return segment

    async with aiohttp.ClientSession() as session:
        segments: list[DataFrame] = await asyncio.gather(*[fetch(url, session)
                                                           for url in urls])
        df = concat(segments)
        return df

# max 1000 entries


async def fetch_api(symbol: str,
                    freq: Freq,
                    start: str,
                    end: str):
    path = '/api/v3/klines'
    url = f'{BASE_ENDPOINT}{path}'
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
        df = await fetch_api('BTCUSDT', '1h', '2023-01-01', '2023-01-10')
        print(df)
    asyncio.run(main())
