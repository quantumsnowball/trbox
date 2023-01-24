from pandas import DataFrame


def verify_ohlcv(ohlcv: DataFrame) -> DataFrame:
    # ensure the window has valid values
    assert isinstance(ohlcv, DataFrame)
    assert ohlcv.index.name == 'Date'
    assert ohlcv.columns.tolist() == ['Open', 'High', 'Low', 'Close', 'Volume']
    assert not ohlcv.isnull().values.any()
    assert not ohlcv.isna().values.any()
    return ohlcv
