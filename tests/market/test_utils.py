import heapq

from pandas import to_datetime

from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.common.utils import trim_ohlcv_by_range_length
from trbox.market.utils import import_yahoo_csv, make_combined_rolling_windows


def test_heapq_merge():
    LEN = 200

    btc = import_yahoo_csv(f'tests/_data_/BTC_bar1day.csv')
    eth = import_yahoo_csv(f'tests/_data_/ETH_bar1day.csv')

    gen_btc = (('BTC', win)
               for win in btc.rolling(LEN)
               if len(win) >= LEN)
    gen_eth = (('ETH', win)
               for win in eth.rolling(LEN)
               if len(win) >= LEN)

    gen = heapq.merge(gen_btc, gen_eth,
                      key=lambda x: x[1].index[-1])
    _, last_df = next(iter(gen))
    for sym, df in gen:
        assert df.index[-1] >= last_df.index[-1]
        last_df = df
        Log.info(Memo(sym, df.index[-1], df.shape))


def test_combined_rolling_windows():
    SYMBOLS = ['BTC', 'ETH']
    LENGTH = 200
    START = to_datetime('2020-01-01')
    END = to_datetime('2021-12-31')

    # data preprocessing
    dfs = {s: import_yahoo_csv(f'tests/_data_/{s}_bar1day.csv')
           for s in SYMBOLS}
    # data validation
    dfs = {s: trim_ohlcv_by_range_length(df, START, END, LENGTH)
           for s, df in dfs.items()}

    dfs = make_combined_rolling_windows(dfs, LENGTH)

    _, last_df = next(iter(dfs))
    for sym, df in dfs:
        assert df.index[-1] >= last_df.index[-1]
        Log.info(Memo(sym, df.index[-1], df.shape))
