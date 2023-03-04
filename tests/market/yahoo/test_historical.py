import asyncio
import itertools
from collections import namedtuple

import pytest
from pandas import DataFrame, Timedelta, to_datetime

from trbox.market.yahoo.historical.windows.use_dl_sqlite_cache import \
    fetch_sqlite

DateTestset = namedtuple('DateSet', 'start end')

SHORTER = DateTestset(
    start=[
        '2022-01-01',
        to_datetime('20220131'),
        '20220120',
        '2022-01-15T00:00:00.000',
    ],
    end=[
        '2023-01-01',
        to_datetime('20230131'),
        '20230120',
        '2023-01-15T00:00:00.000',
    ],
)
LONGER = DateTestset(
    start=[
        '2014-01-01',
        to_datetime('2015-01-01'),
        '20160101',
        '2017-01-01T00:00:00.000',
    ],
    end=[
        '2023-01-01',
        to_datetime('2023-01-10'),
        '20230115',
        '2023-01-18T00:00:00.000',
    ],
)
CRYPTOS = itertools.product(
    ['BTC-USD', 'ETH-USD', 'BNB-USD'],
    SHORTER.start, SHORTER.end,
)
STOCKS = itertools.product(
    ['SPY', 'QQQ', 'TSLA', 'NVDA', 'AMZN', 'AAPL',],
    LONGER.start, LONGER.end,
)
INDICES = itertools.product(
    ['^GSPC', '^IXIC', ],
    LONGER.start, LONGER.end,
)
FOREX = itertools.product(
    ['EURUSD=X', 'GBPUSD=X', 'JPY=X', ],
    SHORTER.start, SHORTER.end,
)
BONDS = itertools.product(
    ['^TNX', ],
    SHORTER.start, SHORTER.end,
)
FREQ = '1d'
ERROR = 5  # days


@pytest.mark.parametrize('symbol, start, end', [
    *CRYPTOS,
    *STOCKS,
    *INDICES,
    *FOREX,
    # *BONDS,
])
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
