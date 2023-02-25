from trbox import Strategy, Trader
from trbox.backtest import Backtest
from trbox.broker.paper import PaperEX
from trbox.event.market import Candlestick
from trbox.market.dummy import DummyPrice
from trbox.strategy.context import Context


def main():
    SYMBOL = 'BTC'
    QUANTITY = 0.2

    # on_tick
    def dummy_action(my: Context):
        result = my.portfolio.trade(SYMBOL, QUANTITY)
        # Log.critical(Memo('see me ?').by(my.strategy))
        print(my.count._i[1])

    bt = Backtest(
        Trader(
            strategy=Strategy(name='Benchmark')
            .on(SYMBOL, Candlestick, do=dummy_action),
            market=DummyPrice(SYMBOL),
            broker=PaperEX(SYMBOL)),
        Trader(
            strategy=Strategy(name='basic')
            .on(SYMBOL, Candlestick, do=dummy_action),
            market=DummyPrice(SYMBOL),
            broker=PaperEX(SYMBOL))
    )

    print('Started backtest')
    bt.run(parallel=False)
    print('Finished backtest')

    bt.result.save(__file__)


if __name__ == '__main__':
    main()
