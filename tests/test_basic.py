from trbox import Strategy, Backtest, Market
from trbox.broker.simulated import PaperEX


def test_dummy():
    class St(Strategy):
        def step(self, e):
            print(f'St: price={e.price}')
            self.runner.broker.trade('BTC', +10)

    bt = Backtest(
        strategy=St(),
        market=Market(),
        broker=PaperEX()
    )

    bt.run()
