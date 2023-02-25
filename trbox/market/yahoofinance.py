from threading import Event

import yfinance as yf
from pandas import DataFrame, Timestamp, to_datetime
from typing_extensions import override

from trbox.common.constants import OHLCV_COLUMN_NAMES
from trbox.common.types import Symbols
from trbox.common.utils import trim_ohlcv_by_range_length
from trbox.event.broker import AuditRequest
from trbox.event.market import OhlcvWindow
from trbox.market import MarketWorker
from trbox.market.utils import make_combined_rolling_windows


def yfinance_download(symbol: str, interval: str) -> DataFrame:
    ticker = yf.Ticker(symbol)
    df = ticker.history(period='max',
                        interval=interval)
    df.index = df.index.tz_localize(None)
    df = df[OHLCV_COLUMN_NAMES]
    print(f'downloaded ohlcv, symbol="{symbol}", shape={df.shape}', flush=True)
    return df


class YahooDL(MarketWorker):
    def __init__(self, *,
                 symbols: Symbols,
                 start: Timestamp | str,
                 end: Timestamp | str | None = None,
                 interval: str = '1d',
                 length: int) -> None:
        super().__init__()
        self._symbols = symbols
        self._start = to_datetime(start)
        self._end = to_datetime(end)
        self._interval = interval
        self._length = length
        # data preprocessing
        self._dfs = {s: yfinance_download(
            s, self._interval) for s in self._symbols}
        # data validation
        self._dfs = {s: trim_ohlcv_by_range_length(df, self._start, self._end, self._length)
                     for s, df in self._dfs.items()}
        # data ready
        self._window_generator = make_combined_rolling_windows(
            self._dfs, self._length)
        # work thread event
        self._alive = Event()

    @override
    def working(self) -> None:
        for symbol, df in self._window_generator:
            hb = self.strategy.heartbeats.get(
                (symbol, OhlcvWindow), None)

            if hb:
                hb.wait(5)

            e = OhlcvWindow(timestamp=df.index[-1],
                            symbol=symbol,
                            win=df)
            self.strategy.put(e)
            self.broker.put(e)
            self.portfolio.put(e)

            # TODO other parties should decide when to audit
            self.broker.put(AuditRequest(e.timestamp))

            if hb:
                hb.clear()

            if not self._alive.is_set():
                return

        # stop iteration
        self.trader.stop()
