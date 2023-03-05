import asyncio
from threading import Event

from pandas import DataFrame, Timedelta, Timestamp, to_datetime
from typing_extensions import override

from trbox.common.types import Symbol, Symbols
from trbox.common.utils import utcnow
from trbox.event.broker import AuditRequest
from trbox.event.market import OhlcvWindow
from trbox.market import MarketWorker
from trbox.market.binance.historical.windows.constants import Freq
from trbox.market.binance.historical.windows.use_dl_sqlite_cache import \
    fetch_sqlite
from trbox.market.utils import make_combined_rolling_windows


def cal_win_start(start: Timestamp, freq: Freq, length: int) -> Timestamp:
    num = int(freq[:-1])*length
    if freq.endswith('d'):
        return start - Timedelta(days=num)
    elif freq.endswith('h'):
        return start - Timedelta(hours=num)
    elif freq.endswith('m'):
        return start - Timedelta(minutes=num)
    elif freq.endswith('s'):
        return start - Timedelta(seconds=num)
    else:
        raise ValueError


class BinanceHistoricalWindows(MarketWorker):
    def __init__(self,
                 symbols: Symbols,
                 start: str | Timestamp,
                 end: str | Timestamp | None,
                 freq: Freq,
                 length: int) -> None:
        super().__init__()
        self._symbols = symbols
        self._start: Timestamp = to_datetime(start)
        self._end = to_datetime(end if end else utcnow())
        self._freq = freq
        self._length = length
        # data preprocessing
        self._win_start = cal_win_start(self._start, self._freq, self._length)
        self._dfs_coros = {s: fetch_sqlite(s, self._freq, self._win_start, self._end)
                           for s in self._symbols}
        # work thread event
        self._alive = Event()

    @ override
    def working(self) -> None:
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

            e = OhlcvWindow(timestamp=df.index[-1],
                            symbol=symbol,
                            win=df)
            self.strategy.put(e)
            self.broker.put(e)
            self.portfolio.put(e)

            self.broker.put(AuditRequest(e.timestamp))

            if hb:
                hb.clear()

            if not self._alive.is_set():
                return

        # stop iteration
        self.trader.stop()
