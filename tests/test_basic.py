from pandas import Timestamp
import pytest
from trbox import Strategy, Trader
from trbox.broker.simulated import PaperEX
from trbox.common.logger import info
from trbox.event.market import OhlcvWindow, Candlestick
from trbox.market import Market
from trbox.market.datasource.onrequest.localcsv import YahooOHLCV
from trbox.market.datasource.streaming.dummy import DummyPrice


@pytest.mark.parametrize('live', [True, False])
def test_dummy(live):
    SYMBOL = 'BTC'

    # on_tick
    def dummy_action(self: Strategy, e: Candlestick):
        assert live == (not self.trader.backtesting)
        info(f'price={e.price}', who=self)
        self.trader.trade(SYMBOL, +10)

    Trader(
        live=live,
        strategy=Strategy(
            on_tick=dummy_action),
        market=Market(
            source=DummyPrice(SYMBOL, delay=0)),
        broker=PaperEX(SYMBOL)
    ).run()


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
        info(f'St: date={e.datetime} last={e.last.shape}, close={e.close}')

    Trader(
        strategy=Strategy(
            on_window=dummy_action),
        market=Market(
            source=YahooOHLCV(
                source={s: f'tests/_data_/{s}_bar1day.csv'
                        for s in SYMBOLS},
                start=start,
                end=end,
                length=length)),
        broker=PaperEX(SYMBOLS[0])
    ).run()
