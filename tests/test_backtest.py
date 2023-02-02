import pytest
from pandas import Series, Timestamp

from trbox import Strategy, Trader
from trbox.backtest import Backtest
from trbox.backtest.result import Result
from trbox.broker.paper import PaperEX
from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.event.market import Candlestick, OhlcvWindow
from trbox.market.onrequest.localcsv import YahooOHLCV
from trbox.market.streaming.dummy import DummyPrice
from trbox.trader.dashboard import Dashboard


@pytest.mark.parametrize('name', [None, 'DummySt', ])
@pytest.mark.parametrize('parallel', [True, False])
def test_dummy(name, parallel):
    SYMBOL = 'BTC'
    DELAY = 0

    # on_tick
    def dummy_action(self: Strategy, e: Candlestick):
        Log.info(Memo(st=self, price=e.price).by(self))
        self.trader.trade(SYMBOL, +10)

    bt = Backtest(
        Trader(
            strategy=Strategy(
                name='Benchmark',
                on_tick=dummy_action),
            market=DummyPrice(SYMBOL, delay=DELAY),
            broker=PaperEX(SYMBOL)),
        Trader(
            strategy=Strategy(
                name=name,
                on_tick=dummy_action),
            market=DummyPrice(SYMBOL, delay=0),
            broker=PaperEX(SYMBOL))
    )
    bt.run(parallel=parallel)
    # for backtesting, up to here means market data finished, simular to user termination
    for trader in bt.traders:
        Log.info(Memo(str(trader.dashboard)).by(trader).tag('dashboard'))
        assert isinstance(trader.dashboard, Dashboard)
    # TODO result should contain all the backtest info for review
    Log.info(Memo(str(bt.result)).by(bt).tag('result'))
    assert isinstance(bt.result, Result)
    # TODO but what about live trading? how to get some report without
    # terminating the Trader?


@pytest.mark.parametrize('start', [Timestamp(2022, 1, 1),])
@pytest.mark.parametrize('end', [Timestamp(2022, 3, 31),])
# @pytest.mark.parametrize('start', [Timestamp(2022, 1, 1), '2022-01-01', None])
# @pytest.mark.parametrize('end', [Timestamp(2022, 3, 31), '2022-3-31', None])
@pytest.mark.parametrize('length', [100, 200, 500])
def test_historical_data(start: Timestamp | str | None,
                         end: Timestamp | str | None,
                         length: int):
    SYMBOLS = ['BTC', 'ETH']
    QUANTITY = 0.2

    # on_window
    def dummy_action(self: Strategy, e: OhlcvWindow):
        assert e.win.shape == (length, 10)
        self.trader.trade(SYMBOLS[0], QUANTITY)
        Log.info(
            f'St: date={e.datetime} last={e.ohlcv.shape}, close={e.close}')

    def trader(name: str):
        return Trader(
            strategy=Strategy(
                name=name,
                on_window=dummy_action),
            market=YahooOHLCV(
                source={s: f'tests/_data_/{s}_bar1day.csv' for s in SYMBOLS},
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
        Log.warning(Memo(t.dashboard.navs.head(20),
                         shape=t.dashboard.navs.shape)
                    .by(t).tag('navs', 'tail'))
    Log.info(Memo(str(bt.result)).by(bt).tag('result'))
    assert isinstance(bt.result, Result)
