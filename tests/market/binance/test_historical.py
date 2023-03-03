import asyncio
import time

import pytest
from pandas import DataFrame, Timestamp, to_datetime

from tests.utils import assert_valid_metrics
from trbox.broker.paper import PaperEX
from trbox.common.logger import Log
from trbox.event.market import OhlcvWindow
from trbox.market.binance.historical.windows import BinanceHistoricalWindows
from trbox.market.binance.historical.windows.use_dl_sqlite_cache import \
    fetch_sqlite
from trbox.market.binance.historical.windows.use_dl_zip_cache import fetch_zip
from trbox.strategy import Strategy
from trbox.strategy.context import Context
from trbox.trader import Trader


@pytest.mark.parametrize('symbol', ['BTCUSDT', 'ETHUSDT', 'BNBUSDT'])
@pytest.mark.parametrize('freq', ['1d', '4h', '2h', '1h', '5m', '1m'])
@pytest.mark.parametrize('start', ['2022-12-01', '2022-12-15',])
@pytest.mark.parametrize('end', ['2023-01-01', '2023-01-15',])
def test_fetch_sqlite(symbol, freq, start, end):
    async def main():
        df = await fetch_sqlite(symbol, freq, start, end)
        assert isinstance(df, DataFrame)
        assert df.shape[1] == 5
        assert df.index.is_monotonic
        assert df.index[0] >= to_datetime(start)
        assert df.index[-1] <= to_datetime(end)
    asyncio.run(main())


"""
time
run: await fetch_zip('BTCUSDT', '1h', '2023-01-01', '2023-03-31')
  sync: ~0.1368s (cached)
  async: ~0.17 (cached)
run: await fetch_zip('BTCUSDT', '1h', '2022-01-01', '2023-01-31')
  sync: ~1.44s (cached)
  async: ~1.95s (cached)
conclusion: sync open is slightly faster than async

run: await fetch_zip('BTCUSDT', '1h', '2022-01-01', '2023-01-31')
  async: 0.101s (cached)
conclusion: use a database is significantly faster (~20 times)
"""


@pytest.mark.playground()
def test_compare():
    async def main():
        await fetch_zip('BTCUSDT', '1h', '2022-01-01', '2023-01-31')
    start_time = time.time()
    asyncio.run(main())
    end_time = time.time()
    Log.warning(f'time delta : {end_time-start_time}')


@pytest.mark.parametrize('start', [Timestamp(2023, 1, 1), '2023-01-01'])
@pytest.mark.parametrize('end', [Timestamp(2023, 1, 31), '2023-1-31'])
@pytest.mark.parametrize('length', [100, 200])
def test_historical_data(start: str | Timestamp,
                         end: str | Timestamp,
                         length: int):
    TARGET = 'BTCUSDT'
    REF = ['ETHUSDT']
    SYMBOLS = (TARGET, *REF)
    FREQ = '1h'

    def for_target(my: Context[OhlcvWindow]):
        if my.count.every(24):
            my.portfolio.rebalance(SYMBOLS[0], 0.5, my.event.price)
        if my.count.every(250):
            assert_valid_metrics(my)

    t = Trader(
        strategy=Strategy(name='historical')
        .on(TARGET, OhlcvWindow, do=for_target),
        market=BinanceHistoricalWindows(
            symbols=SYMBOLS,
            start=start,
            end=end,
            freq=FREQ,
            length=length),
        broker=PaperEX(SYMBOLS)
    )

    t.run()

    assert len(t.dashboard.navs) >= 10
