from abc import ABC
from typing import Any

from typing_extensions import override

from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.common.types import Positions, Symbol
from trbox.event import Event, MarketEvent
from trbox.event.broker import MarketOrder, OrderResult
from trbox.event.handler import CounterParty
from trbox.event.portfolio import (EquityCurveHistoryRequest,
                                   EquityCurveHistoryUpdate, EquityCurveUpdate,
                                   OrderResultUpdate, TradeLogHistoryRequest,
                                   TradeLogHistoryUpdate)
from trbox.portfolio.dashboard import Dashboard
from trbox.portfolio.metrics import Metrics
from trbox.portfolio.stats import Stats


class Portfolio(CounterParty, ABC):
    def __init__(self) -> None:
        super().__init__()
        # TODO How do you control when to log the equity value? should I pass
        # in a user arg and determine from it?
        self._dashboard = Dashboard()
        # maintain a state of account info flags
        self._positions_updated = False

    #
    # account status
    #

    @property
    def cash(self) -> float:
        return self.broker.cash

    @property
    def positions(self) -> Positions:
        return self.broker.positions

    @property
    def equity(self) -> float:
        return self.broker.equity

    #
    # dashboard
    #

    @property
    def dashboard(self) -> Dashboard:
        return self._dashboard

    #
    # analysis
    #

    @property
    def metrics(self) -> Metrics:
        return Metrics(portfolio=self)

    @property
    def stats(self) -> Stats:
        return Stats(portfolio=self)

    #
    # helpers
    #

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
    def handle_market_event(self, e: MarketEvent) -> None:
        # TODO
        # here your will receiving the same price info from Market as Strategy and Broker
        # use it to update the position worth, and update the rolling nav
        # log it to dashboard regularly, and also pass it to console
        self.console.put(EquityCurveUpdate(timestamp=e.timestamp,
                                           equity=self.equity,
                                           positions=self.positions))

    def handle_order_result(self, e: OrderResult) -> None:
        # TODO
        # fetching the position from broker may be expensive and slow in live trading
        # so only need to fetch in the beginnging and then update only after trade result
        self.dashboard.add_trade_record(e)
        self.console.put(OrderResultUpdate(e))

    def handle_equity_curve_history_request(self,
                                            e: EquityCurveHistoryRequest) -> None:
        series = self.dashboard.navs.iloc[-e.n:] \
            if e.n is not None else self.dashboard.navs
        self.console.put(EquityCurveHistoryUpdate(client=e.client,
                                                  series=series))

    def handle_order_result_history_request(self,
                                            e: TradeLogHistoryRequest) -> None:
        df = self.dashboard.trade_records.iloc[-e.n:] \
            if e.n is not None else self.dashboard.trade_records
        self.console.put(TradeLogHistoryUpdate(client=e.client,
                                               df=df))

    @override
    def handle(self, e: Event) -> None:
        if isinstance(e, MarketEvent):
            self.handle_market_event(e)
        elif isinstance(e, OrderResult):
            self.handle_order_result(e)
        elif isinstance(e, EquityCurveHistoryRequest):
            self.handle_equity_curve_history_request(e)
        elif isinstance(e, TradeLogHistoryRequest):
            self.handle_order_result_history_request(e)


class Basic(Portfolio):
    pass
