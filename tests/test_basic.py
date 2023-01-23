import logging
from trbox import Strategy, Trader
from trbox.broker.simulated import PaperEX
from trbox.event.market import Price
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
    Trader(
        strategy=Strategy(),
        market=YahooOHLCV('tests/_data_/BTC_bar1day.csv'),
        broker=PaperEX()
    ).run()
