import os

import pytest
from dotenv import load_dotenv
from pandas import Series

from trbox.broker.binance.testnet import BinanceTestnet
from trbox.broker.paper import PaperEX
from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.common.utils import ppf
from trbox.console.dashboard import TrboxDashboard
from trbox.event.market import TradeTick, KlineTick
from trbox.market.binance.streaming.klines import BinanceStreamingKlines
from trbox.market.binance.streaming.trades import BinanceStreamingTrades
from trbox.strategy import Strategy
from trbox.strategy.context import Context
from trbox.trader import Trader

load_dotenv()
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')


@pytest.mark.playground()
def test_binance_trade_streaming():
    SYMBOL = 'BTCUSDT'
    INTERVAL = 2000

    def handle(my: Context[TradeTick]):
        # dummy trade
        price = my.event.price
        win = my.memory['rolling2000'][2000]
        win.append(my.event.price)
        if my.count.every(INTERVAL):
            pnlr: float = Series(win).rank(pct=True).iloc[-1]
            my.portfolio.rebalance(SYMBOL, pnlr, price)
            Log.info(Memo('counter hit', i=my.count._i, e=ppf(my.event))
                     .by(my.strategy).tag('period', 'regular', f'bar{INTERVAL}').sparse())

    Trader(
        strategy=Strategy(
            name='test-trade-streaming')
        .on(SYMBOL, TradeTick, do=handle),
        market=BinanceStreamingTrades(symbol=SYMBOL),
        broker=PaperEX(SYMBOL),
        console=TrboxDashboard()
    ).run()


@pytest.mark.playground()
def test_binance_kline_streaming():
    SYMBOL = 'BTCUSDT'
    QUANTITY = 0.1

    def handle(my: Context[KlineTick]):
        # buy/sell on every minute on Binance testnet
        quantity = +QUANTITY if my.event.timestamp.minute % 2 == 0 else -QUANTITY
        result = my.portfolio.trade(SYMBOL, quantity)
        Log.warning(Memo(ppf(result)).by(
            my.strategy).tag('trade').sparse())

    Trader(
        strategy=Strategy(
            name='test-kline-streaming')
        .on(SYMBOL, KlineTick, do=handle),
        market=BinanceStreamingKlines(symbol=SYMBOL, interval='1m'),
        broker=BinanceTestnet()
    ).run()
