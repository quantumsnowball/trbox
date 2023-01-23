from trbox import Strategy, Backtest, Market, Broker
import logging


logging.basicConfig(level='INFO')


class St(Strategy):
    def step(self, e):
        print(f'St: price={e.price}')
        self.runner.broker.trade('BTC', +10)


bt = Backtest(
    strategy=St(),
    market=Market(),
    broker=Broker()
)
bt.run()
