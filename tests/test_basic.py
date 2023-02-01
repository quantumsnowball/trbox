from pandas import Timestamp
import pytest
from trbox import Strategy, Trader
from trbox.backtest import Backtest
from trbox.broker.paper import PaperEX
from trbox.common.logger import info
from trbox.common.logger.parser import Log
from trbox.common.utils import cln
from trbox.event.market import OhlcvWindow, Candlestick
from trbox.market.onrequest.localcsv import YahooOHLCV
from trbox.market.streaming.dummy import DummyPrice


@pytest.mark.parametrize('live', [False, True])
@pytest.mark.parametrize('name', [None, 'DummySt'])
def test_dummy(name, live):
    SYMBOL = 'BTC'

    # on_tick
    def dummy_action(self: Strategy, e: Candlestick):
        assert live == (not self.trader.backtesting)
        info(Log(st=self, price=e.price).by(self))
        self.trader.trade(SYMBOL, +10)

    Trader(
        live=live,
        strategy=Strategy(
            name=name,
            on_tick=dummy_action),
        market=DummyPrice(SYMBOL, delay=0),
        broker=PaperEX(SYMBOL)
    ).run()


@pytest.mark.parametrize('name', [None, 'DummySt', ])
@pytest.mark.parametrize('parallel', [True, ])
def test_dummy_batch(name, parallel):
    SYMBOL = 'BTC'

    # on_tick
    def dummy_action(self: Strategy, e: Candlestick):
        info(Log(st=self, price=e.price).by(self))
        self.trader.trade(SYMBOL, +10)

    bt = Backtest(
        Trader(
            strategy=Strategy(
                name='Benchmark',
                on_tick=dummy_action),
            market=DummyPrice(SYMBOL, delay=0),
            broker=PaperEX(SYMBOL)
        ),
        Trader(
            strategy=Strategy(
                name=name,
                on_tick=dummy_action),
            market=DummyPrice(SYMBOL, delay=0),
            broker=PaperEX(SYMBOL)
        )
    )
    result = bt.run(parallel=parallel)
    info(Log(cln(bt), result=result))
    # TODO result should contain all the backtest info for review


@pytest.mark.parametrize('start', [Timestamp(2021, 1, 1), '2020-01-01', None])
@pytest.mark.parametrize('end', [Timestamp(2021, 3, 31), '2021-3-31', None])
@pytest.mark.parametrize('length', [100, 200, 500])
def test_historical_data(start: Timestamp | str | None,
                         end: Timestamp | str | None,
                         length: int):
    SYMBOLS = ['BTC', 'ETH']

    # on_window
    def dummy_action(self: Strategy, e: OhlcvWindow):
        assert e.win.shape == (length, 10)
        self.trader.trade(SYMBOLS[0], +10)
        info(f'St: date={e.datetime} last={e.ohlcv.shape}, close={e.close}')

    Trader(
        strategy=Strategy(
            on_window=dummy_action),
        market=YahooOHLCV(
            source={s: f'tests/_data_/{s}_bar1day.csv'
                    for s in SYMBOLS},
            start=start,
            end=end,
            length=length),
        broker=PaperEX(SYMBOLS)
    ).run()
