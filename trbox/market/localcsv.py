from collections.abc import Generator
from threading import Event, Thread
from typing import Callable

from pandas import DataFrame, Timestamp, to_datetime
from typing_extensions import override

from trbox.common.logger import Log
from trbox.common.types import Symbol, Symbols
from trbox.common.utils import trim_ohlcv_by_range_length
from trbox.event.market import OhlcvWindow
from trbox.market import Market
from trbox.market.utils import import_yahoo_csv, make_combined_rolling_windows


class RollingWindow(Market):
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
    def start(self) -> None:
        def worker() -> None:
            for symbol, df in self._window_generator:
                hb = self.trader.strategy.heartbeats.get(
                    (symbol, OhlcvWindow), None)

                if hb:
                    hb.wait(5)

                self.send.new_market_data(
                    OhlcvWindow(timestamp=df.index[-1],
                                symbol=symbol,
                                win=df))

                if hb:
                    hb.clear()

                if not self._alive.is_set():
                    return

            # stop iteration
            self.trader.stop()

        self._alive.set()
        # only start a thread if for sure Strategy will listen to it
        t = Thread(target=worker)
        t.start()

    @override
    def stop(self) -> None:
        self._alive.clear()
