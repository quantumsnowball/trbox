from datetime import datetime
from time import sleep

import pytest
from pandas import Series, Timestamp

from tests.utils import assert_valid_metrics
from trbox import Strategy, Trader
from trbox.broker.paper import PaperEX
from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.console.dashboard import TrboxDashboard
from trbox.event.market import Candlestick, OhlcvWindow
from trbox.market.generated.historical.trades import GeneratedHistoricalTrades
from trbox.market.local.historical.windows import LocalHistoricalWindows
from trbox.portfolio.dashboard import Dashboard
from trbox.strategy import Context
from trbox.strategy.types import Memroy


@pytest.mark.parametrize('live', [False, True])
@pytest.mark.parametrize('name', [None, 'DummySt'])
# @pytest.mark.parametrize('name, live', [('dummy', False)])
def test_dummy(name, live):
    SYMBOL = 'BTC'
    QUANTITY = 0.2
    INTERVAL = 4
    N = 3000
    DELAY = 0.0

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
        if my.count.every(250):
            assert_valid_metrics(my)
        # can also access dashboard when still trading
        assert isinstance(my.trader.portfolio.dashboard, Dashboard)
        Log.info(Memo('anytime get', dashboard=my.trader.portfolio.dashboard)
                 .by(my.strategy).tag('dashboard'))
        sleep(DELAY)

    t = Trader(
        live=live,
        strategy=Strategy(name=name,)
        .on('BTC', Candlestick, do=dummy_action),
        market=GeneratedHistoricalTrades(SYMBOL, n=N),
        broker=PaperEX(SYMBOL),
        console=TrboxDashboard()
    )
    t.run()
    # up to here the market data terminated, simular to user termination
    Log.info(Memo(str(t.portfolio.dashboard)).by(t).tag('dashboard'))
    assert isinstance(t.portfolio.dashboard, Dashboard)
    assert isinstance(t.portfolio.dashboard.navs, Series)
    if not live:
        assert len(t.portfolio.dashboard.navs) > 0
        assert isinstance(t.portfolio.dashboard.navs.index[-1], datetime)


@pytest.mark.parametrize('start', [Timestamp(2021, 1, 1), '2021-01-01'])
@pytest.mark.parametrize('end', [Timestamp(2021, 3, 31), '2021-3-31', None])
@pytest.mark.parametrize('length', [100, 200, 500])
# @pytest.mark.parametrize('start, end, length', [('2021-01-01', '2021-03-31', 200)])
def test_historical_data(start: Timestamp | str,
                         end: Timestamp | str | None,
                         length: int):
    TARGET = 'BTC'
    REF = ['ETH']
    SYMBOLS = (TARGET, *REF)
    QUANTITY = 0.2

    def no_frontrun(memory: Memroy, e: OhlcvWindow) -> bool:
        timestamp = e.win.index[-1]
        last2 = memory['last2'][2]
        last2.append(timestamp)
        if len(last2) >= 2:
            if not last2[-1] > last2[-2]:
                return False
        return True

    def for_target(my: Context):
        assert isinstance(my.event, OhlcvWindow)
        assert my.event.symbol == TARGET
        assert my.event.win.shape == (length, 5)
        my.portfolio.trade(TARGET, QUANTITY)
        Log.info(Memo(datetime=my.event.timestamp, symbol=my.event.symbol))
        assert no_frontrun(my.memory, my.event)
        if my.count.every(250):
            assert_valid_metrics(my)

    def for_ref(my: Context):
        assert isinstance(my.event, OhlcvWindow)
        assert my.event.symbol == REF[0]
        assert my.event.win.shape == (length, 5)
        my.portfolio.trade(REF[0], QUANTITY)
        Log.info(Memo(datetime=my.event.timestamp, symbol=my.event.symbol))
        assert no_frontrun(my.memory, my.event)
        if my.count.every(250):
            assert_valid_metrics(my)

    t = Trader(
        strategy=Strategy(name='historical')
        .on(TARGET, OhlcvWindow, do=for_target)
        .on(REF[0], OhlcvWindow, do=for_ref),
        market=LocalHistoricalWindows(
            symbols=SYMBOLS,
            source=lambda s: f'tests/_data_/{s}_bar1day.csv',
            start=start,
            end=end,
            length=length),
        broker=PaperEX(SYMBOLS)
    )

    t.run()

    assert len(t.portfolio.dashboard.navs) >= 10
