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
from trbox.market.utils import import_yahoo_csv


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
        self._window_generators: dict[Symbol, Generator[DataFrame, None, None]] = {
            s: (win
                for win in df.rolling(self._length)
                if len(win) >= self._length)
            for s, df in self._dfs.items()
        }
        # work thread event
        self._alive = Event()

    @override
    def start(self) -> None:
        def worker(symbol: Symbol) -> None:
            heartbeat = self.trader._strategy.heartbeats[(symbol, OhlcvWindow)]
            for df in self._window_generators[symbol]:
                heartbeat.wait(5)

                self.send.new_market_data(
                    OhlcvWindow(timestamp=df.index[-1],
                                symbol=symbol,
                                win=df))

                heartbeat.clear()

                if not self._alive.is_set():
                    return

            # stop iteration
            self.trader.stop()

        self._alive.set()
        # only start a thread if for sure Strategy will listen to it
        hooked_symbols = [k[0] for k in self.trader.strategy.heartbeats]
        for s in hooked_symbols:
            t = Thread(target=worker, args=(s, ))
            t.start()

    @override
    def stop(self) -> None:
        self._alive.clear()
