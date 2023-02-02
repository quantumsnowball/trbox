from pandas import Series

from trbox.common.utils import cln


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
        self._nav: float | None = None
        self._navs: list[float] = []
        # trade_log: DataFrame | None = None
        # metrics: dict[str, float] | None = None

    def __str__(self) -> str:
        return f'{cln(self)}({self.desc})'

    @property
    def nav(self) -> float | None:
        return self._nav

    @nav.setter
    def nav(self, val: float) -> None:
        self._nav = val
        self._navs.append(val)

    @property
    def navs(self) -> Series:
        return Series(self._navs, dtype=float)
