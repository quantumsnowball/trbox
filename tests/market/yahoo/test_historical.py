import asyncio
import itertools

import pytest
from pandas import DataFrame, Timedelta, to_datetime

from trbox.market.yahoo.historical.windows.use_dl_sqlite_cache import \
    fetch_sqlite

FREQ = '1d'
CRYPTOS = itertools.product(
    ['BTC-USD', 'ETH-USD', 'BNB-USD'],
    [
        '2022-01-01',
        to_datetime('20220131'),
        '20220120',
        '2022-01-15T00:00:00.000',
    ],
    [
        '2023-01-01',
        to_datetime('20230131'),
        '20230120',
        '2023-01-15T00:00:00.000',
    ],
)
STOCKS = itertools.product(
    ['SPY', 'QQQ', 'TSLA', 'NVDA', 'AMZN', 'AAPL',],
    [
        '2014-01-01',
        to_datetime('2015-01-01'),
        '20160101',
        '2017-01-01T00:00:00.000',
    ],
    [
        '2023-01-01',
        to_datetime('2023-01-10'),
        '20230115',
        '2023-01-18T00:00:00.000',
    ],
)
ERROR = 5  # days


@pytest.mark.parametrize('symbol, start, end', [*CRYPTOS, *STOCKS])
def test_fetch_sqlite(symbol, start, end):
    async def main():
        df = await fetch_sqlite(symbol, FREQ, start, end)
        assert isinstance(df, DataFrame)
        assert df.shape[1] == 5
        assert df.index.is_monotonic_increasing
        start_, end_ = to_datetime(start), to_datetime(end)
        assert start_ <= df.index[0] <= start_ + Timedelta(days=ERROR)
        assert end_ - Timedelta(days=ERROR) <= df.index[-1] <= end_
        for row in df.itertuples(index=False):
            open, high, low, close, *_ = tuple(map(lambda x: round(x, 4), row))
            assert low <= open <= high
            assert low <= close <= high

    asyncio.run(main())
