'''
Ignored by pytest
'''
from trbox import Strategy, Trader
from trbox.broker.simulated import PaperEX
from trbox.common.logging import info
from trbox.event.market import Candlestick
from trbox.market import Market
from trbox.market.datasource.streaming.dummy import DummyPrice
import logging
logging.basicConfig(level='DEBUG')


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
        market=Market(
            source=DummyPrice(SYMBOL, delay=0)),
        broker=PaperEX(SYMBOL)
    ).run()


if __name__ == '__main__':
    test_dummy()
