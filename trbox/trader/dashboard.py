from dataclasses import dataclass

from pandas import Series, Timestamp

from trbox.common.utils import cln


@dataclass
class TradeRecord:
    '''
    Date Symbol Action Quantity 
    Price GrossProceeds Fees NetProceeds
    '''
    ...


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
    desc: str = 'A dashboard provides all info needed to analysis the Trader'

    def __init__(self) -> None:
        self._navs: list[float] = []
        self._navs_index: list[Timestamp] = []

    def __str__(self) -> str:
        return f'{cln(self)}({self.desc})'

    #
    # data
    #
    @property
    def navs(self) -> Series:
        return Series(self._navs, index=self._navs_index, dtype=float)

    #
    # updating
    #

    def add_equity_record(self, timestamp: Timestamp, val: float) -> None:
        self._navs_index.append(timestamp)
        self._navs.append(val)

    def add_trade_record(self) -> None:
        ...

    #
    # analysis
    #

    def metric(self) -> None:
        pass

    #
    # presenting
    #

    def plot(self) -> None:
        # TODO may be simple nav ploting, both live and backtesting
        ...
