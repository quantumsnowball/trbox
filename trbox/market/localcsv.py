from collections.abc import Generator
from threading import Event, Thread

from pandas import DataFrame, Timestamp, to_datetime
from typing_extensions import override

from trbox.common.types import Symbol
from trbox.common.utils import trim_ohlcv_by_range_length
from trbox.event.market import OhlcvWindow
from trbox.market import Market
from trbox.market.utils import import_yahoo_csv


class RollingWindow(Market):
    def __init__(self, *,
                 source: str,
                 symbol: Symbol,
                 start: Timestamp | str,
                 end: Timestamp | str | None = None,
                 length: int) -> None:
        super().__init__()
        self._source = source
        self._symbol = symbol
        self._start = to_datetime(start)
        self._end = to_datetime(end)
        self._length = length
        # data preprocessing
        self._df = import_yahoo_csv(self._source)
        # data validation
        self._df = trim_ohlcv_by_range_length(
            self._df, self._start, self._end, self._length)
        # data ready
        self._window_generator: Generator[DataFrame, None, None] = (
            win
            for win in self._df.rolling(self._length)
            if len(win) >= self._length
        )
        # work thread event
        self._alive = Event()

    @override
    def start(self) -> None:
        def worker() -> None:
            for df in self._window_generator:
                self.trader.signal.heartbeat.wait(5)

                self.send.new_market_data(
                    OhlcvWindow(timestamp=df.index[-1],
                                symbol=self._symbol,
                                win=df))

                self.trader.signal.heartbeat.clear()

                if not self._alive.is_set():
                    return

            # stop iteration
            self.trader.stop()

        self._alive.set()
        t = Thread(target=worker)
        t.start()

    @override
    def stop(self) -> None:
        self._alive.clear()
