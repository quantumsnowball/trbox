from trbox import Strategy, Trader
from trbox.backtest import Backtest
from trbox.backtest.result import Result
from trbox.broker.paper import PaperEX
from trbox.common.logger import Log, set_log_level
from trbox.common.logger.parser import Memo
from trbox.event.market import Candlestick
from trbox.market.dummy import DummyPrice
from trbox.portfolio.dashboard import Dashboard
from trbox.strategy.context import Context

set_log_level('INFO')


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


if __name__ == '__main__':
    main()
