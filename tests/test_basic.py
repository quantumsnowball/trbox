import logging
from trbox import Strategy, Trader
from trbox.broker.simulated import PaperEX
from trbox.market.historical import YahooOHLCV
from trbox.market.simulated import DummyPrice


class DummyStg(Strategy):
    def step(self, e):
        logging.info(f'St: price={e.price}')
        self.runner.broker.trade('BTC', +10)


def test_dummy():
    Trader(
        strategy=DummyStg(),
        market=DummyPrice(delay=0),
        broker=PaperEX()
    ).run()


def test_historical_data():
    assert 1
    Trader(
        strategy=DummyStg(),
        market=YahooOHLCV('tests/_data_/BTC_bar1day.csv'),
        broker=PaperEX()
    ).run()
