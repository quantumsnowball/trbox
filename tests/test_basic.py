import logging
from trbox import Strategy, Trader
from trbox.broker.simulated import PaperEX
from trbox.event.market import OhlcvWindow, Price
from trbox.market.historical import YahooOHLCV
from trbox.market.simulated import DummyPrice


def test_dummy():
    def dummy_action(self: Strategy, e: Price):
        logging.info(f'St: price={e.price}')
        self.runner.broker.trade('BTC', +10)

    Trader(
        strategy=Strategy(on_tick=dummy_action),
        market=DummyPrice(delay=0),
        broker=PaperEX()
    ).run()


def test_historical_data():
    def dummy_action(self: Strategy, e: OhlcvWindow):
        assert e.win.shape == (200, 5)
        self.runner.broker.trade('BTC', +10)
        logging.info(
            f'St: date={e.datetime} last={e.last.shape}, close={e.close}')

    Trader(
        strategy=Strategy(on_window=dummy_action),
        market=YahooOHLCV('tests/_data_/BTC_bar1day.csv', 200),
        broker=PaperEX()
    ).run()
