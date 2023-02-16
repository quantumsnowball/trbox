import threading
from dataclasses import asdict, dataclass

from pandas import DataFrame, Series, Timestamp

from trbox.common.types import Symbol
from trbox.common.utils import cln
from trbox.event.broker import OrderResult


@dataclass
class TradeRecord:
    Date: Timestamp | None
    Symbol: Symbol | None
    Action: str | None
    Quantity: float | None
    Price: float | None
    GrossProceeds: float | None
    Fees: float | None
    NetProceeds: float | None


class Dashboard:
    '''
    In live trading, the run function is normally never return unless exceptions
    raised in the code. This class may be return as long as there the user
    terminated the program, or request a report in the middle of a live trading.
    In backtesting, the end of market data may be treated like an exception of
    a live trading session. In live trading, a user may use another class such as
    Dashboard or Console to send event to handler, and will yield the same Reuslt
    object.
    '''

    def __init__(self) -> None:
        self._navs: list[float] = []
        self._navs_index: list[Timestamp] = []
        self._trade_records: list[TradeRecord] = []
        # locks, make sure thread safetyy
        self._lock_navs = threading.Lock()
        self._lock_trade_records = threading.Lock()

    def __str__(self) -> str:
        return f'{cln(self)}'

    #
    # data
    #
    @property
    def navs(self) -> Series:
        with self._lock_navs:
            return Series(self._navs, index=self._navs_index, dtype=float)

    @property
    def trade_records(self) -> DataFrame:
        with self._lock_trade_records:
            return DataFrame([asdict(r) for r in self._trade_records]).set_index('Date')
    #
    # updating
    #

    def add_equity_record(self, timestamp: Timestamp, val: float) -> None:
        with self._lock_navs:
            self._navs_index.append(timestamp)
            self._navs.append(val)

    def add_trade_record(self, e: OrderResult) -> None:
        with self._lock_trade_records:
            self._trade_records.append(
                TradeRecord(e.timestamp,
                            e.order.symbol,
                            e.action,
                            e.quantity,
                            e.price,
                            e.gross_proceeds,
                            e.fee,
                            e.net_proceeds))

    #
    # presenting
    #

    def plot(self) -> None:
        # TODO may be simple nav ploting, both live and backtesting
        ...
