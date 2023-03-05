from pandas import Series

from trbox import Strategy, Trader
from trbox.backtest import Backtest
from trbox.broker.paper import PaperEX
from trbox.event.market import OhlcvWindow
from trbox.market.binance.historical.windows import BinanceHistoricalWindows
from trbox.strategy.context import Context

SYMBOL = 'BTCUSDT'
SYMBOLS = (SYMBOL, )
START = '2023-01-01'
END = None
FREQ = '1h'
LENGTH = 200
INTERVAL = 24


def buy_hold(my: Context[OhlcvWindow]):
    if my.count.every(INTERVAL):
        my.portfolio.rebalance(SYMBOL, 1.0, my.event.price)


def pnl_ratio(win: Series) -> float:
    pnlr = Series(win.rank(pct=True))
    return pnlr[-1]


def follow_pnl(my: Context[OhlcvWindow]):
    if my.count.every(INTERVAL):
        win = my.event.win['Close']
        pnlr = pnl_ratio(win)
        weight = pnlr
        my.portfolio.rebalance(SYMBOL, weight, my.event.price)


bt = Backtest(
    Trader(
        strategy=Strategy(name='buy-hold')
        .on(SYMBOL, OhlcvWindow, do=buy_hold),
        market=BinanceHistoricalWindows(
            symbols=SYMBOLS,
            start=START,
            end=END,
            freq=FREQ,
            length=LENGTH),
        broker=PaperEX(SYMBOL)),
    Trader(
        strategy=Strategy(name='pnl-ratio')
        .on(SYMBOL, OhlcvWindow, do=follow_pnl),
        market=BinanceHistoricalWindows(
            symbols=SYMBOLS,
            start=START,
            end=END,
            freq=FREQ,
            length=LENGTH),
        broker=PaperEX(SYMBOL))
)

print('Started backtest')
bt.run(parallel=False)
print('Finished backtest')

bt.result.save()
