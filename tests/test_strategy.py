from trbox.broker.paper import PaperEX
from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.market.onrequest.localcsv import YahooOHLCV
from trbox.strategy.presets.benchmark import BuyAndHold
from trbox.trader import Trader


def test_benchmark():
    SYMBOL = 'BTC'
    START = '2021-01-01'
    END = '2021-12-31'
    LENGTH = 200

    t = Trader(
        strategy=BuyAndHold(SYMBOL, 1.0),
        market=YahooOHLCV(
            source={SYMBOL: f'tests/_data_/{SYMBOL}_bar1day.csv'},
            start=START,
            end=END,
            length=LENGTH),
        broker=PaperEX(SYMBOL)
    )

    t.run()

    Log.warning(Memo('Order Result',
                     navs=t.dashboard.navs)
                .tag('dashboard').sparse())
