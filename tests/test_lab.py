import logging
from pprint import pformat as pp
import ccxt
from dotenv import load_dotenv
import os


load_dotenv()


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
