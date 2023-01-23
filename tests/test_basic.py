from trbox import Strategy, Backtest
from trbox.broker.simulated import PaperEX
from trbox.market.simulated import DummyPrice


def test_dummy():
    class St(Strategy):
        def step(self, e):
            print(f'St: price={e.price}')
            self.runner.broker.trade('BTC', +10)

    bt = Backtest(
        strategy=St(),
        market=DummyPrice(),
        broker=PaperEX()
    )

    bt.run()
