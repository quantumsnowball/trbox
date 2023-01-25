import logging
from pprint import pformat as pp
from dotenv import load_dotenv
import os
import asyncio
from binance.client import Client, AsyncClient
from binance import ThreadedWebsocketManager
import pytest


load_dotenv()
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')


@pytest.mark.lab()
def test_binance_restful():
    '''
    It is working, fetch price json without api key
    '''
    def run_sync():
        client = Client()
        # client = Client(API_KEY, API_SECRET, testnet=True)

        def print_exchange_info():
            exinfo = client.get_exchange_info()
            logging.info(pp(exinfo))
        print_exchange_info()

        def print_tick(symbol: str):
            tick = client.get_symbol_ticker(symbol=symbol)
            logging.info(pp(tick))
        print_tick('BTCUSDT')

    run_sync()

    async def run_async():
        # open
        client = await AsyncClient().create()
        # client = await AsyncClient().create(API_KEY, API_SECRET)

        async def print_exchange_info():
            exinfo = await client.get_exchange_info()
            logging.info(pp(exinfo))
        await print_exchange_info()

        async def print_tick(symbol: str):
            tick = await client.get_symbol_ticker(symbol=symbol)
            logging.info(pp(tick))
        await print_tick('BTCUSDT')

        # close
        await client.close_connection()

    asyncio.run(run_async())


@pytest.mark.lab('not working')
def test_binance_websocket():
    '''
    Doesn't work!
    the callback never get called, but debug log said that the msg is received
    '''
    SYMBOL = 'ETHUSDT'

    def run_sync():
        # await asyncio.sleep(1)
        # logging.info('Already slept for 1 seconds.')

        def handle_socket_message(msg):
            logging.info(f"message type: {msg['e']}")
            logging.info(msg)

        bsm = ThreadedWebsocketManager(API_KEY, API_SECRET)
        bsm.start()
        # subscribe to a stream
        bsm.start_symbol_ticker_socket(
            callback=handle_socket_message,
            symbol=SYMBOL
        )

        bsm.join()

    run_sync()
