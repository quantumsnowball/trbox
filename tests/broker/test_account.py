import pytest
from trbox.broker.simulated import PaperEX
from trbox.common.logger import info
from trbox.common.logger.parser import Log
from trbox.market import Market
from trbox.strategy import Strategy
from trbox.trader import Trader
from trbox.market.datasource.streaming.dummy import DummyPrice


@pytest.mark.parametrize('cash', [
    10000, 12345.6789, 1e6, -100, -10000, 1 / 2, ])
def test_account_cash(cash: float):
    SYMBOL = 'CASH'

    def on_tick(self: Strategy, _):
        assert self.trader.cash == cash
        info(Log(cash=self.trader.cash)
             .by(self).tag('initial', 'cash'))

    Trader(
        strategy=Strategy(
            on_tick=on_tick),
        market=Market(
            source=DummyPrice(SYMBOL, delay=0)),
        broker=PaperEX(SYMBOL,
                       initial_fund=cash)
    ).run()
