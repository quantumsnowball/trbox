import pytest
from trbox.broker.simulated import PaperEX
from trbox.common.logger import info
from trbox.common.logger.parser import Log
from trbox.event.market import OhlcvWindow
from trbox.market import Market
from trbox.market.datasource.onrequest.localcsv import YahooOHLCV
from trbox.strategy import Strategy
from trbox.trader import Trader
from trbox.market.datasource.streaming.dummy import DummyPrice


def test_account_trade():
    SYMBOL = 'BTC'
    START = '2021-01-01'
    END = '2021-04-01'
    LENGTH = 200

    def on_window(self: Strategy, _: OhlcvWindow):
        self.trader.trade(SYMBOL, +0.1)
        info(Log('trading',
                 cash=self.trader.cash,
                 position=self.trader.positions[SYMBOL])
             .by(self).tag(SYMBOL).sparse())

    Trader(
        strategy=Strategy(
            on_window=on_window),
        market=Market(
            source=YahooOHLCV(
                source={SYMBOL: f'tests/_data_/{SYMBOL}_bar1day.csv'},
                start=START,
                end=END,
                length=LENGTH)),
        broker=PaperEX(SYMBOL)
    ).run()


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
