from abc import ABC
from typing import Any

from typing_extensions import override

from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.common.types import Symbol
from trbox.event import Event
from trbox.event.broker import MarketOrder
from trbox.event.handler import CounterParty


class Portfolio(CounterParty, ABC):
    def __init__(self) -> None:
        super().__init__()

    # account status

    @property
    def cash(self) -> float:
        return self._broker.cash

    @property
    def positions(self) -> dict[Symbol, float]:
        return self._broker.positions

    @property
    def equity(self) -> float:
        return self._broker.equity

    # helpers

    # TODO
    # these helpers should confirm there is no pending order first
    # otherwise may issue multiple order causing wrong rebalance ratio

    def trade(self, symbol: Symbol, quantity: float) -> dict[str, Any] | None:
        return self.broker.trade(MarketOrder(symbol, quantity))

    def rebalance(self,
                  symbol: Symbol,
                  pct_target: float,
                  ref_price: float,
                  pct_min: float = 0.01) -> None:
        target_value = self.equity * pct_target
        net_value = target_value - self.broker.positions_worth
        if abs(net_value / self.equity) < pct_min:
            return
        target_quantity = net_value / ref_price
        Log.info(Memo(target_quantity=target_quantity)
                 .by(self).sparse())
        self._broker.trade(MarketOrder(symbol, target_quantity))

    def clear(self, _: Symbol) -> None:
        raise NotImplementedError


class DefaultPortfolio(Portfolio):
    @override
    def handle(self, _: Event) -> None:
        pass
