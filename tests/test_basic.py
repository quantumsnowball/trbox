from pandas import Timestamp
import pytest
import logging
from trbox import Strategy, Trader
from trbox.broker.simulated import PaperEX
from trbox.event.market import OhlcvWindow, Candlestick
from trbox.market import Market
from trbox.market.historical import YahooOHLCV
from trbox.market.simulated import DummyPrice


def test_dummy():
    # on_tick
    def dummy_action(self: Strategy, e: Candlestick):
        logging.info(f'St: price={e.price}')
        self.runner.broker.trade('BTC', +10)

    Trader(
        strategy=Strategy(
            on_tick=dummy_action),
        market=Market(
            source=DummyPrice(delay=0)),
        broker=PaperEX()
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
        self.runner.broker.trade(SYMBOLS[0], +10)
        logging.info(
            f'St: date={e.datetime} last={e.last.shape}, close={e.close}')

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
        broker=PaperEX()
    ).run()
