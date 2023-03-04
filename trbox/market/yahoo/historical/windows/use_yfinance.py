import yfinance as yf
from pandas import DataFrame

from trbox.common.constants import OHLCV_COLUMN_NAMES


def yfinance_download(symbol: str, interval: str) -> DataFrame:
    ticker = yf.Ticker(symbol)
    df: DataFrame = ticker.history(period='max',
                                   interval=interval)
    df = DataFrame(df.tz_localize(None))
    df = df[OHLCV_COLUMN_NAMES]
    print(f'downloaded ohlcv, symbol="{symbol}", shape={df.shape}', flush=True)
    return df
