import os

import pytest
from dotenv import load_dotenv

from trbox.broker.paper import PaperEX
from trbox.event.market import Candlestick
from trbox.market.streaming.binance import BinanceWebsocket
from trbox.strategy import Strategy
from trbox.trader import Trader

load_dotenv()
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')


@pytest.mark.lab()
def test_binance():
    SYMBOL = 'BTCUSDT'

    def handle(self: Strategy, _: Candlestick):
        # dummy trade
        self.trader.trade(SYMBOL, +9)

    Trader(
        strategy=Strategy(
            on_tick=handle),
        market=BinanceWebsocket(symbol=SYMBOL),
        broker=PaperEX(SYMBOL)
    ).run()
