from trbox.broker.paper import PaperEX
from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.market.local.historical.windows import LocalHistoricalWindows
from trbox.strategy.presets.benchmark import BuyAndHold
from trbox.trader import Trader


def test_benchmark():
    SYMBOL = 'BTC'
    START = '2021-01-01'
    END = '2021-12-31'
    LENGTH = 200

    t = Trader(
        strategy=BuyAndHold(SYMBOL, 1.0, name='Benchmark'),
        market=LocalHistoricalWindows(
            symbols=(SYMBOL,),
            source=lambda s: f'tests/_data_/{s}_bar1day.csv',
            start=START,
            end=END,
            length=LENGTH),
        broker=PaperEX(SYMBOL)
    )

    t.run()

    assert len(t.dashboard.navs) >= 10

    Log.warning(Memo('Order Result',
                     navs=t.dashboard.navs)
                .tag('dashboard').sparse())
