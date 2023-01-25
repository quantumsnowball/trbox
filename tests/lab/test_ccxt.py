import logging
from pprint import pformat as pp
import ccxt
from dotenv import load_dotenv
import os
import pytest


load_dotenv()
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')


@pytest.mark.lab()
def test_ccxt():
    # logging.info(pp(ccxt.exchanges))
    binance = ccxt.binance()
    cex_id = binance.id
    markets = binance.load_markets()
    btcusdt = markets['BTC/USDT']
    logging.info(pp(cex_id))
    logging.info(pp(btcusdt))
    logging.info(os.getenv('API_KEY'))
    logging.info(os.getenv('API_SECRET'))
