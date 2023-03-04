import pytest

from trbox.broker.paper import PaperEX
from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.event.market import OhlcvWindow, TradeTick
from trbox.market.generated.historical.trades import GeneratedHistoricalTrades
from trbox.market.yahoo.historical.windows import YahooHistoricalWindows
from trbox.strategy import Strategy
from trbox.strategy.context import Context
from trbox.trader import Trader


def test_account_trade():
    SYMBOL = 'BTC-USD'
    START = '2021-01-01'
    END = '2021-04-01'
    LENGTH = 200

    def on_window(my: Context[OhlcvWindow]):
        my.portfolio.trade(SYMBOL, +0.2)
        Log.info(Memo('trading',
                      cash=my.portfolio.cash,
                      position=my.portfolio.positions[SYMBOL],
                      equity=my.portfolio.equity)
                 .by(my.strategy).tag(SYMBOL).sparse())

    Trader(
        strategy=Strategy(
            name='TestAccountTrade')
        .on(SYMBOL, OhlcvWindow, do=on_window),
        market=YahooHistoricalWindows(
            symbols=(SYMBOL, ),
            start=START,
            end=END,
            length=LENGTH),
        broker=PaperEX(SYMBOL)
    ).run()


@pytest.mark.parametrize('cash', [
    10000, 12345.6789, 1e6, -100, -10000, 1 / 2, ])
def test_account_cash(cash: float):
    SYMBOL = 'CASH'

    def on_tick(my: Context[TradeTick]):
        assert my.portfolio.cash == cash
        Log.info(Memo(cash=my.portfolio.cash)
                 .by(my.strategy).tag('initial', 'cash'))

    Trader(
        strategy=Strategy(
            name='TestAccountCash')
        .on(SYMBOL, TradeTick, do=on_tick),
        market=GeneratedHistoricalTrades(SYMBOL),
        broker=PaperEX(SYMBOL,
                       initial_fund=cash)
    ).run()
