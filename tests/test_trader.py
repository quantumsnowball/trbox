import pytest
from pandas import Timestamp

from trbox import Strategy, Trader
from trbox.broker.paper import PaperEX
from trbox.common.logger import info
from trbox.common.logger.parser import Log
from trbox.event.market import Candlestick, OhlcvWindow
from trbox.market.onrequest.localcsv import YahooOHLCV
from trbox.market.streaming.dummy import DummyPrice
from trbox.trader.dashboard import Dashboard


@pytest.mark.parametrize('live', [False, True])
@pytest.mark.parametrize('name', [None, 'DummySt'])
def test_dummy(name, live):
    SYMBOL = 'BTC'
    DELAY = 0

    # on_tick
    def dummy_action(self: Strategy, e: Candlestick):
        assert live == (not self.trader.backtesting)
        info(Log(st=self, price=e.price).by(self))
        self.trader.trade(SYMBOL, +10)
        # can also access dashboard when still trading
        assert isinstance(trader.dashboard, Dashboard)
        info(Log('anytime get', dashboard=self.trader.dashboard)
             .by(self).tag('dashboard'))

    trader = Trader(
        live=live,
        strategy=Strategy(
            name=name,
            on_tick=dummy_action),
        market=DummyPrice(SYMBOL, delay=DELAY),
        broker=PaperEX(SYMBOL)
    )
    trader.run()
    # up to here the market data terminated, simular to user termination
    info(Log(str(trader.dashboard)).by(trader).tag('dashboard'))
    assert isinstance(trader.dashboard, Dashboard)


@pytest.mark.parametrize('start', [Timestamp(2021, 1, 1), '2021-01-01', None])
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
