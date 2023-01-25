import os
from logging import info
from dotenv import load_dotenv
from trbox.broker.simulated import PaperEX
from trbox.market import Market
from trbox.market.datasource.streaming.binance import BinanceRestful

from trbox.runner import Trader
from trbox.strategy import Strategy

load_dotenv()
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')


def test_binance():
    def handle():
        info('handling')

    Trader(
        strategy=Strategy(),
        market=Market(
            source=BinanceRestful()),
        broker=PaperEX()
    ).run()
