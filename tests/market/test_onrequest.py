import os
import logging
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')


def test_binance():
    logging.info('deving test_binance')
