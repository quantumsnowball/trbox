from pandas import DataFrame, Timestamp
from trbox.common.constants import OHLCV_COLUMN_NAMES


def verify_ohlcv(ohlcv: DataFrame) -> DataFrame:
    # ensure the window has valid values
    assert isinstance(ohlcv, DataFrame)
    assert ohlcv.index.name == 'Date'
    assert (ohlcv.columns.levels[1] == OHLCV_COLUMN_NAMES).all()
    assert not ohlcv.isnull().any().any()
    assert not ohlcv.isna().any().any()
    return ohlcv


def trim_ohlcv_by_range_length(
        df: DataFrame,
        start: Timestamp | None,
        end: Timestamp | None,
        length: int) -> DataFrame:
    '''
    given a dataframe, start, end and length, check the validity of all
    inputs, trim the dataframe correctly to be used in datasource generator,
    '''
    # check if the config make sense
    assert len(df) > length
    if start and end:
        assert start < end
    # find the correct trim_from date
    trim_from = df.loc[:start].iloc[-length:].index[0]
    # trim_to date is the end date
    trim_to = end
    # applyy trim and return df
    df = df.loc[trim_from:trim_to]
    return df
