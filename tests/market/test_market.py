import os

import pytest
from dotenv import load_dotenv

from trbox.broker.paper import PaperEX
from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
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

    def handle(self: Strategy, _: Candlestick):
        # dummy trade
        self.trader.trade(SYMBOL, 0.01)

    Trader(
        strategy=Strategy(
            on_tick=handle),
        market=BinanceTradeStreaming(symbol=SYMBOL),
        broker=PaperEX(SYMBOL)
    ).run()


@pytest.mark.lab()
def test_binance_kline_streaming():
    SYMBOL = 'BTCUSDT'

    def handle(self: Strategy, e: Kline):
        # dummy trade
        # self.trader.trade(SYMBOL, 1)
        if e.bar_finished:
            Log.warning(Memo(e).sparse())

    Trader(
        strategy=Strategy(
            on_kline=handle),
        market=BinanceKlineStreaming(symbol=SYMBOL, interval='1m'),
        broker=PaperEX(SYMBOL)
    ).run()
