from __future__ import annotations

from typing import TYPE_CHECKING

from pandas import Timestamp

from trbox.event import MarketEvent
from trbox.event.broker import AuditRequest, OrderResult

if TYPE_CHECKING:
    from trbox.broker import Broker
    from trbox.market import Market
    from trbox.strategy import Strategy
    from trbox.trader import Trader


class Distributor:
    '''
    Distributor has a basket of helper function to route the event to
    appropriate parties.
    '''

    def __init__(self,
                 trader: Trader,
                 *,
                 strategy: Strategy,
                 market: Market,
                 broker: Broker) -> None:
        self._trader = trader
        self._strategy = strategy
        self._market = market
        self._broker = broker

    #
    # event routing
    #
