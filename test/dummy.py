from trbox import Strategy, Backtest, Market


class St(Strategy):
    pass


bt = Backtest(
    strategy=St(),
    market=Market()
)
bt.run()
