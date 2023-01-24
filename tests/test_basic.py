import pytest
import logging
from trbox import Strategy, Trader
from trbox.broker.simulated import PaperEX
from trbox.event.market import OhlcvWindow, Price
from trbox.market import Market
from trbox.market.historical import YahooOHLCV
from trbox.market.simulated import DummyPrice


def test_dummy():
    def dummy_action(self: Strategy, e: Price):
        logging.info(f'St: price={e.price}')
        self.runner.broker.trade('BTC', +10)

    Trader(
        strategy=Strategy(
            on_tick=dummy_action),
        market=Market(
            source=DummyPrice(delay=0)),
        broker=PaperEX()
    ).run()


@pytest.mark.parametrize('win_size', [100, 200, 500])
def test_historical_data(win_size: int):
    SYMBOLS = ['BTC', 'ETH']

    def dummy_action(self: Strategy, e: OhlcvWindow):
        assert e.win.shape == (win_size, 10)
        self.runner.broker.trade('BTC', +10)
        logging.info(
            f'St: date={e.datetime} last={e.last.shape}, close={e.close}')

    Trader(
        strategy=Strategy(
            on_window=dummy_action),
        market=Market(
            source=YahooOHLCV(
                source={s: f'tests/_data_/{s}_bar1day.csv'
                        for s in SYMBOLS},
                length=win_size)),
        broker=PaperEX()
    ).run()
