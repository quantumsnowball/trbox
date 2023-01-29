import pytest
import os
from dotenv import load_dotenv
from trbox.broker.paper import PaperEX
from trbox.event.market import Candlestick
from trbox.market import Market
from trbox.market.datasource.streaming.binance import BinanceWebsocket
from trbox.trader import Trader
from trbox.strategy import Strategy

load_dotenv()
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')


@pytest.mark.lab()
def test_binance():
    SYMBOL = 'BTCUSDT'

    def handle(self: Strategy, e: Candlestick):
        # dummy trade
        self.trader.trade(SYMBOL, +9)

    Trader(
        strategy=Strategy(
            on_tick=handle),
        market=Market(
            source=BinanceWebsocket(
                symbol=SYMBOL)),
        broker=PaperEX(SYMBOL)
    ).run()
