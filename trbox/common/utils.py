from pandas import DataFrame
from trbox.common.constants import OHLCV_COLUMN_NAMES


def verify_ohlcv(ohlcv: DataFrame) -> DataFrame:
    # ensure the window has valid values
    assert isinstance(ohlcv, DataFrame)
    assert ohlcv.index.name == 'Date'
    assert (ohlcv.columns.levels[1] == OHLCV_COLUMN_NAMES).all()
    assert not ohlcv.isnull().any().any()
    assert not ohlcv.isna().any().any()
    return ohlcv
