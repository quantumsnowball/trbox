import pytest
from pandas import Series, Timestamp

from trbox import Strategy, Trader
from trbox.backtest import Backtest
from trbox.backtest.result import Result
from trbox.broker.paper import PaperEX
from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.event.market import OhlcvWindow, TradeTick
from trbox.market.generated.historical.trades import GeneratedHistoricalTrades
from trbox.market.yahoo.historical.windows import YahooHistoricalWindows
from trbox.portfolio.dashboard import Dashboard
from trbox.strategy.context import Context


@pytest.mark.parametrize('name', [None, 'DummySt', ])
@pytest.mark.parametrize('mode', ['serial', 'thread', 'process', ])
def test_dummy(name, mode):
    SYMBOL = 'BTC'
    QUANTITY = 0.2

    # on_tick
    def dummy_action(my: Context[TradeTick]):
        my.portfolio.trade(SYMBOL, QUANTITY)

    bt = Backtest(
        Trader(
            strategy=Strategy(name='Benchmark')
            .on(SYMBOL, TradeTick, do=dummy_action),
            market=GeneratedHistoricalTrades(SYMBOL),
            broker=PaperEX(SYMBOL)),
        Trader(
            strategy=Strategy(name=name)
            .on(SYMBOL, TradeTick, do=dummy_action),
            market=GeneratedHistoricalTrades(SYMBOL),
            broker=PaperEX(SYMBOL))
    )
    bt.run(mode=mode)
    # for backtesting, up to here means market data finished, simular to user termination
    for trader in bt.traders:
        Log.info(Memo(str(trader.portfolio.dashboard)).by(
            trader).tag('dashboard'))
        assert isinstance(trader.portfolio.dashboard, Dashboard)
    # result contains all the backtest info for review
    Log.info(Memo(str(bt.result)).by(bt).tag('result'))
    assert isinstance(bt.result, Result)


@pytest.mark.parametrize('start', [Timestamp(2022, 1, 1), '2022-01-01'])
@pytest.mark.parametrize('end', [Timestamp(2022, 3, 31), '2022-3-31', None])
@pytest.mark.parametrize('length', [100, 200, 500])
def test_historical_data(start: Timestamp | str,
                         end: Timestamp | str | None,
                         length: int):
    SYMBOLS = ('BTC-USD', 'ETH-USD')
    SYMBOL = SYMBOLS[0]
    QUANTITY = 0.2

    # on_window
    def dummy_action(my: Context[OhlcvWindow]):
        e = my.event
        assert e.win.shape == (length, 5)
        my.portfolio.trade(SYMBOL, QUANTITY)
        Log.info(Memo(date=e.datetime, shape=e.win.shape, close=e.close)
                 .by(my.strategy))

    def trader(name: str):
        return Trader(
            strategy=Strategy(name=name)
            .on(SYMBOL, OhlcvWindow, do=dummy_action),
            market=YahooHistoricalWindows(
                symbols=SYMBOLS,
                start=start,
                end=end,
                length=length),
            broker=PaperEX(SYMBOLS)
        )
    bt = Backtest(
        trader('Benchmark'),
        trader('DummySt')
    )
    bt.run()

    for t in bt.traders:
        assert isinstance(t.dashboard, Dashboard)
        assert isinstance(t.dashboard.navs, Series)
        assert len(t.dashboard.navs) >= 10
        Log.warning(Memo(t.dashboard.navs.head(20),
                         shape=t.dashboard.navs.shape)
                    .by(t).tag('navs', 'tail'))
    Log.info(Memo(str(bt.result)).by(bt).tag('result'))
    assert isinstance(bt.result, Result)
