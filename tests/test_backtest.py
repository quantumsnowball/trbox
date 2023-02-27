import pytest
from pandas import Series, Timestamp

from trbox import Strategy, Trader
from trbox.backtest import Backtest
from trbox.backtest.result import Result
from trbox.broker.paper import PaperEX
from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.event.market import Candlestick, OhlcvWindow
from trbox.market.dummy import DummyPrice
from trbox.market.local.windows.historical import LocalWindowsHistorical
from trbox.portfolio.dashboard import Dashboard
from trbox.strategy.context import Context


@pytest.mark.parametrize('name', [None, 'DummySt', ])
@pytest.mark.parametrize('parallel', [False, ])
def test_dummy(name, parallel):
    SYMBOL = 'BTC'
    QUANTITY = 0.2

    # on_tick
    def dummy_action(my: Context):
        my.portfolio.trade(SYMBOL, QUANTITY)

    bt = Backtest(
        Trader(
            strategy=Strategy(name='Benchmark')
            .on(SYMBOL, Candlestick, do=dummy_action),
            market=DummyPrice(SYMBOL),
            broker=PaperEX(SYMBOL)),
        Trader(
            strategy=Strategy(name=name)
            .on(SYMBOL, Candlestick, do=dummy_action),
            market=DummyPrice(SYMBOL),
            broker=PaperEX(SYMBOL))
    )
    bt.run(parallel=parallel)
    # for backtesting, up to here means market data finished, simular to user termination
    for trader in bt.traders:
        Log.info(Memo(str(trader.portfolio.dashboard)).by(
            trader).tag('dashboard'))
        assert isinstance(trader.portfolio.dashboard, Dashboard)
    # TODO result should contain all the backtest info for review
    Log.info(Memo(str(bt.result)).by(bt).tag('result'))
    assert isinstance(bt.result, Result)
    # TODO but what about live trading? how to get some report without
    # terminating the Trader?


@pytest.mark.parametrize('start', [Timestamp(2022, 1, 1), '2022-01-01'])
@pytest.mark.parametrize('end', [Timestamp(2022, 3, 31), '2022-3-31', None])
@pytest.mark.parametrize('length', [100, 200, 500])
def test_historical_data(start: Timestamp | str,
                         end: Timestamp | str | None,
                         length: int):
    SYMBOLS = ('BTC', 'ETH')
    SYMBOL = SYMBOLS[0]
    QUANTITY = 0.2

    # on_window
    def dummy_action(my: Context):
        e = my.event
        assert isinstance(e, OhlcvWindow)
        assert e.win.shape == (length, 5)
        my.portfolio.trade(SYMBOL, QUANTITY)
        Log.info(Memo(date=e.datetime, shape=e.ohlcv.shape, close=e.close)
                 .by(my.strategy))

    def trader(name: str):
        return Trader(
            strategy=Strategy(name=name)
            .on(SYMBOL, OhlcvWindow, do=dummy_action),
            market=LocalWindowsHistorical(
                symbols=SYMBOLS,
                source=lambda s: f'tests/_data_/{s}_bar1day.csv',
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
        assert isinstance(t.portfolio.dashboard, Dashboard)
        assert isinstance(t.portfolio.dashboard.navs, Series)
        assert len(t.portfolio.dashboard.navs) >= 10
        Log.warning(Memo(t.portfolio.dashboard.navs.head(20),
                         shape=t.portfolio.dashboard.navs.shape)
                    .by(t).tag('navs', 'tail'))
    Log.info(Memo(str(bt.result)).by(bt).tag('result'))
    assert isinstance(bt.result, Result)
