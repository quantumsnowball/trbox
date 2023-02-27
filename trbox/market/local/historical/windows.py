from threading import Event
from typing import Callable

from pandas import Timestamp, to_datetime
from typing_extensions import override

from trbox.common.types import Symbols
from trbox.common.utils import trim_ohlcv_by_range_length
from trbox.event.broker import AuditRequest
from trbox.event.market import OhlcvWindow
from trbox.market import MarketWorker
from trbox.market.utils import import_yahoo_csv, make_combined_rolling_windows


class LocalHistoricalWindows(MarketWorker):
    def __init__(self, *,
                 source: Callable[[str], str],
                 symbols: Symbols,
                 start: Timestamp | str,
                 end: Timestamp | str | None = None,
                 length: int) -> None:
        super().__init__()
        self._symbols = symbols
        self._source = {s: source(s) for s in self._symbols}
        self._start = to_datetime(start)
        self._end = to_datetime(end)
        self._length = length
        # data preprocessing
        self._dfs = {s: import_yahoo_csv(self._source[s])
                     for s in self._symbols}
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
