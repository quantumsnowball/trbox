from datetime import datetime
from time import sleep

import pytest
from pandas import Series

from trbox import Strategy, Trader
from trbox.broker.paper import PaperEX
from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.console.dashboard import TrboxDashboard
from trbox.event.market import Candlestick
from trbox.market.dummy import DummyPrice
from trbox.portfolio.dashboard import Dashboard
from trbox.strategy import Context


# a slow running server for debug and testing purpose
@pytest.mark.playground()
@pytest.mark.parametrize('name, live', [('dummy', False)])
def test_dev(name, live):
    SYMBOL = 'BTC'
    QUANTITY = 0.2
    INTERVAL = 4
    N = 3000
    DELAY = 0.5

    # on_tick
    def dummy_action(my: Context):
        assert live == (not my.trader.backtesting)
        assert my.event is not None
        assert my.event.symbol == SYMBOL
        if my.count.beginning:
            Log.info('absolute beginning')
        if my.count.every(INTERVAL):
            if not live:
                my.portfolio.trade(SYMBOL, QUANTITY)
            # Log.info(Memo(f'every {INTERVAL}', i=my.count._i).by(
            #     my.strategy).tag('count'))
        # can also access dashboard when still trading
        assert isinstance(my.trader.dashboard, Dashboard)
        Log.info(Memo('anytime get', dashboard=my.trader.dashboard)
                 .by(my.strategy).tag('dashboard'))
        sleep(DELAY)

    t = Trader(
        live=live,
        strategy=Strategy(name=name,)
        .on('BTC', Candlestick, do=dummy_action),
        market=DummyPrice(SYMBOL, n=N),
        broker=PaperEX(SYMBOL),
        console=TrboxDashboard()
    )
    t.run()
    # up to here the market data terminated, simular to user termination
    Log.info(Memo(str(t.dashboard)).by(t).tag('dashboard'))
    assert isinstance(t.dashboard, Dashboard)
    assert isinstance(t.dashboard.navs, Series)
    if not live:
        assert len(t.dashboard.navs) > 0
        assert isinstance(t.dashboard.navs.index[-1], datetime)
