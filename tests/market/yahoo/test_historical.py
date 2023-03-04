import asyncio
import itertools

import pytest
from pandas import DataFrame, to_datetime

from trbox.market.yahoo.historical.windows.use_dl_sqlite_cache import \
    fetch_sqlite

FREQ = '1d'
CRYPTOS = itertools.product(
    ['BTC-USD', 'ETH-USD', 'BNB-USD'],
    ['2022-01-01', '2022-01-31',],
    ['2023-01-01', '2023-01-31',],
)
STOCKS = itertools.product(
    ['SPY', 'QQQ', 'TSLA', 'NVDA', 'AMZN', 'AAPL',],
    ['2010-01-01', '2015-01-31',],
    ['2023-01-01', '2023-01-31',],
)


@pytest.mark.parametrize('symbol, start, end', [*CRYPTOS, *STOCKS])
def test_fetch_sqlite(symbol, start, end):
    async def main():
        df = await fetch_sqlite(symbol, FREQ, start, end)
        assert isinstance(df, DataFrame)
        assert df.shape[1] == 5
        assert df.index.is_monotonic_increasing
        assert df.index[0] >= to_datetime(start)
        assert df.index[-1] <= to_datetime(end)
        for row in df.itertuples(index=False):
            open, high, low, close, *_ = tuple(map(lambda x: round(x, 4), row))
            assert low <= open <= high
            assert low <= close <= high

    asyncio.run(main())
