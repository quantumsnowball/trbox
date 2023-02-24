import time

from trbox import Strategy, Trader
from trbox.backtest import Backtest
from trbox.broker.paper import PaperEX
from trbox.event.market import OhlcvWindow
from trbox.market.localcsv import RollingWindow
from trbox.strategy.context import Context


def main():
    SYMBOL = 'BTC'
    SYMBOLS = ('BTC', )
    START = '2021-07-01'
    END = '2021-12-31'
    LENGTH = 30

    # on_window
    def rebalance(pct_target: float):
        def routine(my: Context):
            assert isinstance(my.event, OhlcvWindow)
            if my.count.every(30):
                my.portfolio.rebalance(SYMBOL, pct_target, my.event.close)
            print('routine done, sleeping ...', flush=True)
            time.sleep(1)
        return routine

    bt = Backtest(
        Trader(
            strategy=Strategy(name='Benchmark')
            .on(SYMBOL, OhlcvWindow, do=rebalance(1)),
            market=RollingWindow(
                symbols=SYMBOLS,
                source=lambda s: f'.data/{s}_bar1day.csv',
                start=START,
                end=END,
                length=LENGTH),
            broker=PaperEX(SYMBOL)),
        Trader(
            strategy=Strategy(name='basic')
            .on(SYMBOL, OhlcvWindow, do=rebalance(0.5)),
            market=RollingWindow(
                symbols=SYMBOLS,
                source=lambda s: f'.data/{s}_bar1day.csv',
                start=START,
                end=END,
                length=LENGTH),
            broker=PaperEX(SYMBOL))
    )

    print('Started backtest')
    bt.run(parallel=False)
    print('Finished backtest')

    bt.result.save(__file__)


if __name__ == '__main__':
    main()
