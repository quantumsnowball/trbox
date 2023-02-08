from abc import ABC
from typing import Any

from typing_extensions import override

from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.common.types import Symbol
from trbox.event import Event, MarketEvent
from trbox.event.broker import MarketOrder, OrderResult
from trbox.event.handler import CounterParty
from trbox.portfolio.dashboard import Dashboard


class Portfolio(CounterParty, ABC):
    def __init__(self) -> None:
        super().__init__()
        # TODO How do you control when to log the equity value? should I pass
        # in a user arg and determine from it?
        self._dashboard = Dashboard()
        # maintain a state of account info flags
        self._positions_updated = False

    # account status

    @property
    def cash(self) -> float:
        return self.broker.cash

    @property
    def positions(self) -> dict[Symbol, float]:
        return self.broker.positions

    @property
    def equity(self) -> float:
        return self.broker.equity

    # dashboard

    @property
    def dashboard(self) -> Dashboard:
        return self._dashboard
        # TODO I think user should be able to request the dashboard as long as
        # the Trader is still running. It should contain the lastest trading
        # result regardless live trading or backtesting.

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

    # handle events
    def handle_market_event(self, e: MarketEvent):
        # TODO
        # here your will receiving the same price info from Market as Strategy and Broker
        # use it to update the position worth, and update the rolling nav
        # log it to dashboard regularly, and also pass it to console
        pass

    def handle_order_result(self, e: OrderResult):
        # TODO
        # fetching the position from broker may be expensive and slow in live trading
        # so only need to fetch in the beginnging and then update only after trade result
        pass

    @override
    def handle(self, e: Event) -> None:
        if isinstance(e, MarketEvent):
            self.handle_market_event(e)
        if isinstance(e, OrderResult):
            self.handle_order_result(e)


class Basic(Portfolio):
    pass
