from typing import Literal

from pandas import to_datetime
from typing_extensions import override

from trbox.common.types import Symbols
from trbox.market import MarketWorker

Freq = Literal['1s',
               '1m', '3m', '5m', '15m', '30m',
               '1h', '2h', '4h', '6h', '8h', '12h',
               '1d', ]


class BinanceHistoricalWindows(MarketWorker):
    def __init__(self,
                 symbols: Symbols,
                 start: str,
                 end: str,
                 freq: Freq,
                 length: int) -> None:
        super().__init__()
        self._symbols = symbols
        self._start = to_datetime(start)
        self._end = to_datetime(end)
        self._freq = freq
        self._length = length

    @override
    def working(self) -> None:
        pass
