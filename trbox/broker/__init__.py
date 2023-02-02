from abc import ABC, abstractmethod

from trbox.common.types import Symbol
from trbox.event import Event
from trbox.event.broker import AuditRequest, Order
from trbox.event.handler import CounterParty


class Broker(CounterParty, ABC):
    '''
    A broker provide some basic operation for the Trader to:
        1) view the state of account, mainly is cash and positions
        2) change the state of account, usually trade (or deposit/withdraw)
    These props and methods should be as realistic as possible. E.g. trader
    must not be able to write to the cash and positions props directly through
    the Strateg class. Instead, cash and position are read only props. Also,
    broker should provide basic trading methods for Trader to use.
    '''

    def __init__(self) -> None:
        super().__init__()
        self._cash: float
        self._positions: dict[Symbol, float]

    def handle(self, e: Event) -> None:
        if isinstance(e, Order):
            self.trade(e)
        if isinstance(e, AuditRequest):
            self.send.new_audit_result(e.timestamp, self.equity)

    #
    # account status
    #
    # TODO in live trading these account status should all be Promise-like
    # objects, and should be resolved in async fashion, need to refactor

    @property
    @abstractmethod
    def cash(self) -> float:
        pass

    @property
    @abstractmethod
    def positions(self) -> dict[Symbol, float]:
        pass

    @property
    @abstractmethod
    def positions_worth(self) -> float:
        pass

    @property
    @abstractmethod
    def equity(self) -> float:
        pass

    #
    # trade operations
    #
    @abstractmethod
    def trade(self, e: Order) -> None:
        pass
