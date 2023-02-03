from datetime import datetime
from time import sleep

import pytest
from pandas import Series, Timestamp

from trbox import Strategy, Trader
from trbox.broker.paper import PaperEX
from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.event.market import Candlestick, OhlcvWindow
from trbox.market.dummy import DummyPrice
from trbox.market.localcsv import RollingWindow
from trbox.trader.dashboard import Dashboard


@pytest.mark.parametrize('live', [False, True])
@pytest.mark.parametrize('name', [None, 'DummySt'])
# @pytest.mark.parametrize('name, live', [('dummy', True)])
def test_dummy(name, live):
    SYMBOL = 'BTC'
    QUANTITY = 0.2

    # on_tick
    def dummy_action(self: Strategy, _: Candlestick):
        assert live == (not self.trader.backtesting)
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
        market=DummyPrice(SYMBOL),
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
# @pytest.mark.parametrize('start, end, length', [('2021-01-01', '2021-03-31', 200)])
def test_historical_data(start: Timestamp | str,
                         end: Timestamp | str | None,
                         length: int):
    SYMBOLS = ['BTC', 'ETH']
    QUANTITY = 0.2

    # on_window
    def dummy_action(self: Strategy, e: OhlcvWindow):
        assert e.win.shape == (length, 10)
        self.trader.trade(SYMBOLS[0], QUANTITY)

    t = Trader(
        strategy=Strategy(
            on_window=dummy_action),
        market=RollingWindow(
            source={s: f'tests/_data_/{s}_bar1day.csv'
                    for s in SYMBOLS},
            start=start,
            end=end,
            length=length),
        broker=PaperEX(SYMBOLS)
    )

    t.run()

    assert len(t.dashboard.navs) >= 10
