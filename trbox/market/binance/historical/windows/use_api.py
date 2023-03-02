import json

import aiohttp
from pandas import DataFrame, to_datetime

from trbox.common.constants import OHLCV_INDEX_NAME
from trbox.market.binance.historical.windows.constants import (
    API_BASE, RAW_COLUMNS, SELECTED_COLUMNS, Freq)


async def fetch_api(symbol: str,
                    freq: Freq,
                    start: str,
                    end: str) -> DataFrame:
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
            df = DataFrame(content, columns=RAW_COLUMNS)
            df = df[SELECTED_COLUMNS]
            df = df.rename(columns={'CloseTime': OHLCV_INDEX_NAME})
            df = df.set_index(OHLCV_INDEX_NAME)
            df.index = to_datetime(df.index.values*1e6).round('S')
            df = df.sort_index()
            return df
