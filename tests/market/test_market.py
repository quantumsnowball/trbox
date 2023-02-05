import os

import pytest
from dotenv import load_dotenv
from pandas import to_datetime

from trbox.broker.binance.testnet import BinanceTestnet
from trbox.broker.paper import PaperEX
from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.common.utils import ppf
from trbox.event.market import Candlestick, Kline
from trbox.market.binance.kline import BinanceKlineStreaming
from trbox.market.binance.trade import BinanceTradeStreaming
from trbox.strategy import Strategy
from trbox.trader import Trader

load_dotenv()
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')


@pytest.mark.lab()
def test_binance_trade_streaming():
    SYMBOL = 'BTCUSDT'

    def handle(self: Strategy, e: Candlestick):
        # dummy trade
        # self.trader.trade(SYMBOL, 0.01)
        if self.count.every(20):
            Log.warning(Memo('counter hit', i=self.count.i, e=ppf(e))
                        .by(self).tag('period', 'regular').sparse())

    Trader(
        strategy=Strategy(
            on_tick=handle),
        market=BinanceTradeStreaming(symbol=SYMBOL),
        broker=PaperEX(SYMBOL)
    ).run()


@pytest.mark.lab()
def test_binance_kline_streaming():
    SYMBOL = 'BTCUSDT'
    QUANTITY = 0.1

    def handle(self: Strategy, e: Kline):
        # buy/sell on every minute on Binance testnet
        if e.bar_finished:
            quantity = +QUANTITY if e.timestamp.minute % 2 == 0 else -QUANTITY
            result = self.trader.trade(SYMBOL, quantity)
            Log.warning(Memo(ppf(result)).by(self).tag('trade').sparse())

    Trader(
        strategy=Strategy(
            on_kline=handle),
        market=BinanceKlineStreaming(symbol=SYMBOL, interval='1m'),
        broker=BinanceTestnet()
    ).run()
