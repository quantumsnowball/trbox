import asyncio

import pytest
from pandas import DataFrame, to_datetime

from trbox.market.yahoo.historical.windows.use_dl_sqlite_cache import \
    fetch_sqlite


@pytest.mark.parametrize('symbol', ['BTC-USD', 'ETH-USD', 'BNB-USD'])
@pytest.mark.parametrize('freq', ['1d', ])
@pytest.mark.parametrize('start', ['2022-01-01', '2022-01-31',])
@pytest.mark.parametrize('end', ['2023-01-01', '2023-01-31',])
def test_fetch_sqlite(symbol, freq, start, end):
    async def main():
        df = await fetch_sqlite(symbol, freq, start, end)
        assert isinstance(df, DataFrame)
        assert df.shape[1] == 5
        assert df.index.is_monotonic_increasing
        assert df.index[0] >= to_datetime(start)
        assert df.index[-1] <= to_datetime(end)
        for open, high, low, close, *_ in df.itertuples(index=False):
            assert low <= open <= high
            assert low <= close <= high

    asyncio.run(main())
