import heapq
from typing import Generator, Iterator

from pandas import DataFrame, Timestamp, concat, read_csv

from trbox.common.constants import OHLCV_COLUMN_NAMES, OHLCV_INDEX_NAME
from trbox.common.types import Symbol


def import_yahoo_csv(path: str) -> DataFrame:
    df = read_csv(path,
                  index_col='Date',
                  parse_dates=True)
    if 'Close' in df.columns and 'Adj Close' in df.columns:
        df.drop('Close', axis=1, inplace=True)
        df.rename({'Adj Close': 'Close'}, axis=1, inplace=True)
    return df


def concat_dfs_by_columns(dfs: dict[Symbol, DataFrame]) -> DataFrame:
    df = concat(dfs, axis=1)
    df.dropna(inplace=True)
    assert not df.isnull().any().any()
    assert not df.isna().any().any()
    assert (df.columns.levels[0] == list(dfs)).all()
    assert (df.columns.levels[1] == OHLCV_COLUMN_NAMES).all()
    assert df.index.name == OHLCV_INDEX_NAME
    return df


def make_combined_rolling_windows(
    dfs: dict[Symbol, DataFrame],
    length: int
) -> Iterator[tuple[Symbol, DataFrame]]:
    def gen_win(sym: Symbol, df: DataFrame) -> Generator[tuple[Symbol, DataFrame], None, None]:
        for win in df.rolling(length):
            if len(win) >= length:
                yield (sym, win)

    def sort_using(x: tuple[Symbol, DataFrame]) -> Timestamp:
        obj: Timestamp = x[1].index[-1]
        return obj

    combined = heapq.merge(*(gen_win(sym, df.sort_index())
                             for sym, df in dfs.items()),
                           key=sort_using)
    return iter(combined)
