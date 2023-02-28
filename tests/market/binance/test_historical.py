import asyncio
import time

import pytest
from pandas import DataFrame

from trbox.common.logger import Log
from trbox.market.binance.historical.windows.use_dl_sqlite_cache import \
    fetch_sqlite
from trbox.market.binance.historical.windows.use_dl_zip_cache import fetch_zip


@pytest.mark.parametrize('symbol', ['BTCUSDT', 'ETHUSDT', 'BNBUSDT'])
@pytest.mark.parametrize('freq', ['1d', '4h', '2h', '1h', '5m', '1m'])
@pytest.mark.parametrize('start', ['2022-12-01', '2023-01-01',])
@pytest.mark.parametrize('end', ['2022-12-15', '2023-01-15',])
def test_fetch_sqlite(symbol, freq, start, end):
    async def main():
        df = await fetch_sqlite(symbol, freq, start, end)
        assert isinstance(df, DataFrame)
        assert df.shape[1] == 5
        assert df.index.is_monotonic
    asyncio.run(main())


@pytest.mark.playground()
def test_compare():
    async def main():
        await fetch_zip('BTCUSDT', '1h', '2022-01-01', '2023-01-31')
    start_time = time.time()
    asyncio.run(main())
    end_time = time.time()
    Log.warning(f'time delta : {end_time-start_time}')
    # time
    # run: await fetch_zip('BTCUSDT', '1h', '2023-01-01', '2023-03-31')
    #   sync: ~0.1368s (cached)
    #   async: ~0.17 (cached)
    # run: await fetch_zip('BTCUSDT', '1h', '2022-01-01', '2023-01-31')
    #   sync: ~1.44s (cached)
    #   async: ~1.95s (cached)
    # conclusion: sync open is slightly faster than async
    #
    # run: await fetch_zip('BTCUSDT', '1h', '2022-01-01', '2023-01-31')
    #   async: 0.101s (cached)
    # conclusion: use a database is significantly faster (~20 times)
