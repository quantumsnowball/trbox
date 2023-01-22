from trbox import Strategy, Backtest, Market


class St(Strategy):
    def step(self, e):
        print(f'St: price={e.price}')


bt = Backtest(
    strategy=St(),
    market=Market()
)
bt.run()
