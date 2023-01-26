from typing import Self
from trbox.trader import Trader


class DataSource:
    '''
    DataSource is not a EventHandler, and does not have any event queue.
    It handles data for Market, and can access runner for putting events
    to other handlers.
    '''

    def attach(self, trader: Trader) -> Self:
        self._trader = trader
        return self

    @property
    def trader(self) -> Trader:
        return self._trader
