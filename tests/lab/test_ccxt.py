import os
from pprint import pformat as pp

import ccxt
import pytest
from dotenv import load_dotenv

from trbox.common.logger import info

load_dotenv()
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")


@pytest.mark.lab()
def test_ccxt():
    # info(pp(ccxt.exchanges))
    binance = ccxt.binance()
    cex_id = binance.id
    markets = binance.load_markets()
    btcusdt = markets["BTC/USDT"]
    info(pp(cex_id))
    info(pp(btcusdt))
    info(os.getenv("API_KEY"))
    info(os.getenv("API_SECRET"))
