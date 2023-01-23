import logging
from trbox import Strategy, Trader
from trbox.broker.simulated import PaperEX
from trbox.market.simulated import DummyPrice


class DummyStg(Strategy):
    def step(self, e):
        logging.info(f'St: price={e.price}')
        self.runner.broker.trade('BTC', +10)


def test_dummy():
    bt = Trader(
        strategy=DummyStg(),
        market=DummyPrice(delay=0),
        broker=PaperEX()
    )

    bt.run()


def test_historical_data():
    pass
