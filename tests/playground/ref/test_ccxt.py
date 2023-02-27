import os
from pprint import pformat as pp

import ccxt
import pytest
from dotenv import load_dotenv

from trbox.common.logger import Log

load_dotenv()
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')


@pytest.mark.playground()
def test_ccxt():
    # info(pp(ccxt.exchanges))
    binance = ccxt.binance()
    cex_id = binance.id
    markets = binance.load_markets()
    btcusdt = markets['BTC/USDT']
    Log.info(pp(cex_id))
    Log.info(pp(btcusdt))
    Log.info(os.getenv('API_KEY'))
    Log.info(os.getenv('API_SECRET'))
