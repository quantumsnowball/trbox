from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Self

from trbox.event.handler import EventHandler

if TYPE_CHECKING:
    from trbox.broker import Broker
    from trbox.console import Console
    from trbox.market import Market
    from trbox.portfolio import Portfolio
    from trbox.strategy import Strategy
    from trbox.trader import Trader


class CounterParty(EventHandler, ABC):
    '''
    Middle class that is attached to a Trader
    '''

    def __init__(self) -> None:
        super().__init__()

    # CounterParty must attach to a Trader to function properly
    def attach(self: Self, *,
               trader: Trader,
               strategy: Strategy,
               market: Market,
               broker: Broker,
               portfolio: Portfolio,
               console: Console,) -> Self:
        self._trader = trader
        self._strategy = strategy
        self._market = market
        self._broker = broker
        self._portfolio = portfolio
        self._console = console
        return self

    @property
    def trader(self) -> Trader:
        return self._trader

    @property
    def strategy(self) -> Strategy:
        return self._strategy

    @property
    def market(self) -> Market:
        return self._market

    @property
    def broker(self) -> Broker:
        return self._broker

    @property
    def portfolio(self) -> Portfolio:
        return self._portfolio

    @property
    def console(self) -> Console:
        return self._console
