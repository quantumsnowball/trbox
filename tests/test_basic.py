from trbox import Strategy, Backtest
from trbox.broker.simulated import PaperEX
from trbox.market.simulated import DummyPrice


def test_dummy():
    class TeStSt(Strategy):
        def step(self, e):
            print(f'St: price={e.price}')
            self.runner.broker.trade('BTC', +10)

    bt = Backtest(
        strategy=TeStSt(),
        market=DummyPrice(delay=0),
        broker=PaperEX()
    )

    bt.run()
