from datetime import datetime

import pytest
from pandas import Series, Timestamp

from trbox import Strategy, Trader
from trbox.broker.paper import PaperEX
from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.event.market import Candlestick, OhlcvWindow
from trbox.market.onrequest.localcsv import YahooOHLCV
from trbox.market.streaming.dummy import DummyPrice
from trbox.trader.dashboard import Dashboard


@pytest.mark.parametrize('live', [False, True])
@pytest.mark.parametrize('name', [None, 'DummySt'])
def test_dummy(name, live):
    SYMBOL = 'BTC'
    QUANTITY = 0.2
    DELAY = 0

    # on_tick
    def dummy_action(self: Strategy, e: Candlestick):
        assert live == (not self.trader.backtesting)
        Log.info(Memo(st=self, price=e.price).by(self))
        self.trader.trade(SYMBOL, QUANTITY)
        # can also access dashboard when still trading
        assert isinstance(self.trader.dashboard, Dashboard)
        Log.info(Memo('anytime get', dashboard=self.trader.dashboard)
                 .by(self).tag('dashboard'))

    t = Trader(
        live=live,
        strategy=Strategy(
            name=name,
            on_tick=dummy_action),
        market=DummyPrice(SYMBOL, delay=DELAY),
        broker=PaperEX(SYMBOL)
    )
    t.run()
    # up to here the market data terminated, simular to user termination
    Log.info(Memo(str(t.dashboard)).by(t).tag('dashboard'))
    assert isinstance(t.dashboard, Dashboard)
    assert isinstance(t.dashboard.navs, Series)
    if not live:
        assert len(t.dashboard.navs) > 0
        assert isinstance(t.dashboard.navs.index[-1], datetime)


@pytest.mark.parametrize('start', [Timestamp(2021, 1, 1), '2021-01-01'])
@pytest.mark.parametrize('end', [Timestamp(2021, 3, 31), '2021-3-31', None])
@pytest.mark.parametrize('length', [100, 200, 500])
def test_historical_data(start: Timestamp | str,
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

    t = Trader(
        strategy=Strategy(
            on_window=dummy_action),
        market=YahooOHLCV(
            source={s: f'tests/_data_/{s}_bar1day.csv'
                    for s in SYMBOLS},
            start=start,
            end=end,
            length=length),
        broker=PaperEX(SYMBOLS)
    )

    t.run()

    assert len(t.dashboard.navs) >= 10
