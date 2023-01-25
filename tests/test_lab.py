import logging
from pprint import pformat as pp
import ccxt
from dotenv import load_dotenv
import os
import asyncio
from binance.client import Client, AsyncClient


load_dotenv()
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')


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


def test_binance():
    def run_sync():
        client = Client(API_KEY, API_SECRET, testnet=True)
        exinfo = client.get_exchange_info()
        logging.info(pp(exinfo))

    # run_sync()

    async def run_async():
        client = await AsyncClient().create(API_KEY, API_SECRET)

        async def print_exchange_info():
            exinfo = await client.get_exchange_info()
            logging.info(pp(exinfo))
        # await print_exchange_info()

        async def print_tick(symbol: str):
            tick = await client.get_symbol_ticker(symbol=symbol)
            logging.info(pp(tick))
        await print_tick('BTCUSDT')

        await client.close_connection()

    asyncio.run(run_async())
