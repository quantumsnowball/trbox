from __future__ import annotations

from typing import TYPE_CHECKING

from trbox.event.broker import OrderResult

if TYPE_CHECKING:
    from trbox.broker import Broker
    from trbox.market import Market
    from trbox.strategy import Strategy
    from trbox.trader import Trader

from trbox.event.market import MarketData, MarketDataRequest


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

    # event routing
    def new_market_data(self, e: MarketData) -> None:
        self._strategy.put(e)
        # if backtesting, broker also receive MarketData to simulate quote
        if self._trader.backtesting:
            self._broker.put(e)
        # TODO in live trading these market data all comes in random times
        # maybe I can monitor the market event timestamp here, calc the time
        # diff, if equal or exceed user arg input, then log a new value.

    def new_market_data_request(self, e: MarketDataRequest) -> None:
        self._market.put(e)

    def new_order_result(self, e: OrderResult) -> None:
        self._strategy.put(e)

    def end_of_market_data(self) -> None:
        self._trader.stop()
