'''
Ignored by pytest
'''
from trbox import Strategy, Trader
from trbox.broker.paper import PaperEX
from trbox.common.logger import Log, set_log_level
from trbox.event.market import Candlestick
from trbox.market.generated.historical.trades import GeneratedHistoricalTrades

set_log_level('DEBUG')


def test_dummy():
    SYMBOL = 'BTC'
    QUANTITY = 0.2

    # on_tick
    def dummy_action(self: Strategy, e: Candlestick):
        Log.info(f'St: price={e.price}')
        self.portfolio.trade(SYMBOL, QUANTITY)

    Trader(
        live=False,
        strategy=Strategy(
            on_tick=dummy_action),
        market=GeneratedHistoricalTrades(SYMBOL),
        broker=PaperEX(SYMBOL)
    ).run()

    Log.debug('demo completed')
    Log.warning('demo completed')
    Log.error('demo completed')
    Log.critical('demo completed')


if __name__ == '__main__':
    test_dummy()
