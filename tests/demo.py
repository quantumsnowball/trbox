'''
Ignored by pytest
'''
from trbox import Strategy, Trader
from trbox.broker.paper import PaperEX
from trbox.common.logger import debug, info, warning, error, critical
from trbox.common.logger import set_log_level
from trbox.event.market import Candlestick
from trbox.market.streaming.dummy import DummyPrice


set_log_level('DEBUG')


def test_dummy():
    SYMBOL = 'BTC'

    # on_tick
    def dummy_action(self: Strategy, e: Candlestick):
        info(f'St: price={e.price}')
        self.trader.trade(SYMBOL, +10)

    Trader(
        live=False,
        strategy=Strategy(
            on_tick=dummy_action),
        market=DummyPrice(SYMBOL, delay=0),
        broker=PaperEX(SYMBOL)
    ).run()

    debug('demo completed')
    warning('demo completed')
    error('demo completed')
    critical('demo completed')


if __name__ == '__main__':
    test_dummy()
