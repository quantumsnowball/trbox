from typing import TypeVar
from trbox.event.distributor import Distributor
from trbox.trader import Trader

Self = TypeVar('Self', bound='DataSource')


class DataSource:
    '''
    DataSource is not a EventHandler, and does not have any event queue.
    It handles data for Market, and can access runner for putting events
    to other handlers.
    '''

    def attach(self: Self, trader: Trader) -> Self:
        self._trader = trader
        return self

    @property
    def trader(self) -> Trader:
        return self._trader

    @property
    def send(self) -> Distributor:
        return self._trader._distributor
