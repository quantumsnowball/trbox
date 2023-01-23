from trbox import Strategy, Backtest
from trbox.broker.simulated import PaperEX
from trbox.market.simulated import DummyPrice


class TeStSt(Strategy):
    def step(self, e):
        print(f'St: price={e.price}')
        self.runner.broker.trade('BTC', +10)


def test_dummy():
    bt = Backtest(
        strategy=TeStSt(),
        market=DummyPrice(delay=0),
        broker=PaperEX()
    )

    bt.run()


def test_historical_data():
    pass
