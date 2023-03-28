import asyncio
from threading import Event

from pandas import DataFrame, Timedelta, Timestamp, to_datetime
from typing_extensions import override

from trbox.backtest.monitor import Tracker
from trbox.common.types import Symbol, Symbols
from trbox.common.utils import utcnow
from trbox.event.broker import AuditRequest
from trbox.event.market import OhlcvWindow
from trbox.market import MarketWorker
from trbox.market.utils import make_combined_rolling_windows
from trbox.market.yahoo.historical.windows.constants import Freq
from trbox.market.yahoo.historical.windows.use_dl_sqlite_cache import \
    fetch_sqlite


def cal_win_start(start: Timestamp, freq: Freq, length: int) -> Timestamp:
    num = int(freq[:-1])*length
    if freq.endswith('d'):
        return start - Timedelta(days=num)
    else:
        raise ValueError


class YahooHistoricalWindows(MarketWorker):
    def __init__(self, *,
                 symbols: Symbols,
                 start: Timestamp | str,
                 end: Timestamp | str | None = None,
                 freq: Freq = '1d',
                 length: int) -> None:
        super().__init__()
        self._symbols = symbols
        self._start = to_datetime(start)
        self._end = to_datetime(end if end else utcnow())
        self._freq: Freq = freq
        self._length = length
        # work thread event
        self._alive = Event()
        # tracker
        self._tracker = Tracker(self._start, self._end)

    @override
    def working(self) -> None:
        # data preprocessing
        self._win_start = cal_win_start(self._start, self._freq, self._length)
        self._dfs_coros = {s: fetch_sqlite(s, self._freq, self._win_start, self._end)
                           for s in self._symbols}
        # gather dfs

        async def gather_dfs() -> dict[Symbol, DataFrame]:
            results = await asyncio.gather(*self._dfs_coros.values())
            return dict(zip(self._symbols, results))
        self._dfs = asyncio.run(gather_dfs())
        # data ready
        self._window_generator = make_combined_rolling_windows(
            self._dfs, self._length)
        # start generator
        for symbol, df in self._window_generator:
            hb = self.strategy.heartbeats.get(
                (symbol, OhlcvWindow), None)

            if hb:
                hb.wait(5)
                hb.clear()

            # TODO first timestamp is one day before self._start, bug?
            e = OhlcvWindow(timestamp=df.index[-1],
                            symbol=symbol,
                            win=df)
            self.strategy.put(e)
            self.broker.put(e)
            self.portfolio.put(e)

            # update progress
            self._tracker.update(self.strategy.name, e.timestamp)

            # TODO other parties should decide when to audit
            self.broker.put(AuditRequest(e.timestamp))

            if not self._alive.is_set():
                return

        # stop iteration
        self.trader.stop()
