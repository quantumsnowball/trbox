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
from trbox.strategy.context import Context
from trbox.trader import Trader

load_dotenv()
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')


@pytest.mark.lab()
def test_binance_trade_streaming():
    SYMBOL = 'BTCUSDT'

    def handle(my: Context):
        # dummy trade
        # self.trader.trade(SYMBOL, 0.01)
        if my.count.every(20):
            Log.warning(Memo('counter hit', i=my.count._i, e=ppf(my.event))
                        .by(my.strategy).tag('period', 'regular').sparse())

    Trader(
        strategy=Strategy()
        .on(SYMBOL, Candlestick, do=handle),
        market=BinanceTradeStreaming(symbol=SYMBOL),
        broker=PaperEX(SYMBOL)
    ).run()


@pytest.mark.lab()
def test_binance_kline_streaming():
    SYMBOL = 'BTCUSDT'
    QUANTITY = 0.1

    def handle(my: Context):
        # buy/sell on every minute on Binance testnet
        if isinstance(my.event, Kline):
            quantity = +QUANTITY if my.event.timestamp.minute % 2 == 0 else -QUANTITY
            result = my.trader.trade(SYMBOL, quantity)
            Log.warning(Memo(ppf(result)).by(
                my.strategy).tag('trade').sparse())

    Trader(
        strategy=Strategy()
        .on(SYMBOL, Kline, do=handle),
        market=BinanceKlineStreaming(symbol=SYMBOL, interval='1m'),
        broker=BinanceTestnet()
    ).run()
