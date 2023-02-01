from pandas import DataFrame, concat, read_csv

from trbox.common.constants import OHLCV_COLUMN_NAMES, OHLCV_INDEX_NAME
from trbox.common.types import Symbol


def import_yahoo_csv(path: str) -> DataFrame:
    df = read_csv(path, index_col="Date", parse_dates=True)
    if "Close" in df.columns and "Adj Close" in df.columns:
        df.drop("Close", axis=1, inplace=True)
        df.rename({"Adj Close": "Close"}, axis=1, inplace=True)
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
