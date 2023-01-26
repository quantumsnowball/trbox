from logging import info
from typing_extensions import override
from trbox.broker import Broker
from trbox.event import Event
from trbox.event.broker import Trade
from trbox.event.market import Candlestick


class PaperEX(Broker):
    def trade(self, e: Trade) -> None:
        info(f'Trade: {e.quantity} {e.symbol}')
        # TODO should have access to MarketData to simulate an execution price
        # TODO adjust Account position and cash balance
        # TODO simulate a Fill/Failed event

    @override
    def handle(self, e: Event) -> None:
        super().handle(e)
        # handle MarketData event when backtesting
        if self.trader.backtesting:
            if isinstance(e, Candlestick):
                info(f'Simulating quote={e.price}')
