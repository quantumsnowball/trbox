from time import sleep

import pytest

from trbox.broker.paper import PaperEX
from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.event.market import OhlcvWindow
from trbox.market.dummy import DummyPrice
from trbox.market.localcsv import RollingWindow
from trbox.strategy import Strategy
from trbox.trader import Trader


def test_account_trade():
    SYMBOL = 'BTC'
    START = '2021-01-01'
    END = '2021-04-01'
    LENGTH = 200

    def on_window(self: Strategy, _: OhlcvWindow):
        self.trader.trade(SYMBOL, +0.2)
        Log.info(Memo('trading',
                      cash=self.trader.cash,
                      position=self.trader.positions[SYMBOL],
                      equity=self.trader.equity)
                 .by(self).tag(SYMBOL).sparse())

    Trader(
        strategy=Strategy(
            on_window=on_window),
        market=RollingWindow(
            source={SYMBOL: f'tests/_data_/{SYMBOL}_bar1day.csv'},
            start=START,
            end=END,
            length=LENGTH),
        broker=PaperEX(SYMBOL)
    ).run()


@pytest.mark.parametrize('cash', [
    10000, 12345.6789, 1e6, -100, -10000, 1 / 2, ])
def test_account_cash(cash: float):
    SYMBOL = 'CASH'

    def on_tick(self: Strategy, _):
        assert self.trader.cash == cash
        Log.info(Memo(cash=self.trader.cash)
                 .by(self).tag('initial', 'cash'))

    Trader(
        strategy=Strategy(
            on_tick=on_tick),
        market=DummyPrice(SYMBOL),
        broker=PaperEX(SYMBOL,
                       initial_fund=cash)
    ).run()
