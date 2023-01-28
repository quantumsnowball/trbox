from abc import ABC, abstractmethod
from trbox.common.types import Symbol
from trbox.event import Event
from trbox.event.broker import Order
from trbox.event.handler import CounterParty


class Account(ABC):
    '''
    An Account should at least support querying the current cash and positions
    info. Only the Broker class should have write access to their states
    directly.

    Because a live trading Account subclass is also sharing this interface,
    only the read-only property is included. This allows a paper trading
    Account to implement setters for them if necessary.
    '''
    @property
    @abstractmethod
    def cash(self) -> float:
        pass

    @property
    @abstractmethod
    def positions(self) -> dict[Symbol, float]:
        pass


class Broker(CounterParty, ABC):
    '''
    A broker provide some basic operation for the Trader. These props and
    methods should be as realistic as possible. E.g. trader must not be able to
    write to the cash and positions props directly through the Strateg class.
    Instead, broker should provide some fund management and trading methods for
    Trader to change their Account states.
    '''

    def __init__(self) -> None:
        super().__init__()
        self._account: Account

    def handle(self, e: Event) -> None:
        if isinstance(e, Order):
            self.trade(e)

    @property
    @abstractmethod
    def account(self) -> Account:
        pass

    @abstractmethod
    def trade(self, e: Order) -> None:
        pass
