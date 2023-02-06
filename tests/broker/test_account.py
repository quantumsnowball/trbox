import pytest

from trbox.broker.paper import PaperEX
from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.event.market import Candlestick, OhlcvWindow
from trbox.market.dummy import DummyPrice
from trbox.market.localcsv import RollingWindow
from trbox.strategy import Strategy
from trbox.strategy.context import Context
from trbox.trader import Trader


def test_account_trade():
    SYMBOL = 'BTC'
    START = '2021-01-01'
    END = '2021-04-01'
    LENGTH = 200

    def on_window(my: Context):
        my.trader.trade(SYMBOL, +0.2)
        Log.info(Memo('trading',
                      cash=my.trader.cash,
                      position=my.trader.positions[SYMBOL],
                      equity=my.trader.equity)
                 .by(my.strategy).tag(SYMBOL).sparse())

    Trader(
        strategy=Strategy()
        .on(SYMBOL, OhlcvWindow, do=on_window),
        market=RollingWindow(
            symbols=(SYMBOL, ),
            source=lambda s: f'tests/_data_/{s}_bar1day.csv',
            start=START,
            end=END,
            length=LENGTH),
        broker=PaperEX(SYMBOL)
    ).run()


@pytest.mark.parametrize('cash', [
    10000, 12345.6789, 1e6, -100, -10000, 1 / 2, ])
def test_account_cash(cash: float):
    SYMBOL = 'CASH'

    def on_tick(my: Context):
        assert my.trader.cash == cash
        Log.info(Memo(cash=my.trader.cash)
                 .by(my.strategy).tag('initial', 'cash'))

    Trader(
        strategy=Strategy()
        .on(SYMBOL, Candlestick, do=on_tick),
        market=DummyPrice(SYMBOL),
        broker=PaperEX(SYMBOL,
                       initial_fund=cash)
    ).run()
