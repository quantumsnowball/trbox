from collections.abc import Generator
from threading import Thread

from pandas import DataFrame, Timestamp, to_datetime
from typing_extensions import override

from trbox.common.types import Symbol
from trbox.common.utils import trim_ohlcv_by_range_length
from trbox.event.market import OhlcvWindow
from trbox.market import Market
from trbox.market.utils import concat_dfs_by_columns, import_yahoo_csv


class RollingWindow(Market):
    def __init__(self, *,
                 source: dict[Symbol, str],
                 start: Timestamp | str,
                 end: Timestamp | str | None = None,
                 length: int) -> None:
        super().__init__()
        self._source = source
        self._symbols = tuple(self._source.keys())
        self._start = to_datetime(start)
        self._end = to_datetime(end)
        self._length = length
        # data preprocessing
        dfs = {s: import_yahoo_csv(p) for s, p in self._source.items()}
        self._df = concat_dfs_by_columns(dfs)
        # data validation
        self._df = trim_ohlcv_by_range_length(
            self._df, self._start, self._end, self._length)
        # data ready
        self._window_generator: Generator[DataFrame, None, None] = (
            win
            for win in self._df.rolling(self._length)
            if len(win) >= self._length
        )
        # TODO to be removed
        self._keep_alive = False

    @override
    def start(self) -> None:
        def worker():
            for df in self._window_generator:
                self.send.new_market_data(
                    OhlcvWindow(df.index[-1], self._symbols, df))

                self.trader.heartbeat.clear()

                if not self._keep_alive:
                    break

                self.trader.heartbeat.wait()
            # stop iteration
            self.trader.stop()

        self._keep_alive = True
        t = Thread(target=worker)
        t.start()

    @override
    def stop(self) -> None:
        self._keep_alive = False
