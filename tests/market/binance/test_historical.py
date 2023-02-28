import asyncio
import time

from trbox.common.logger import Log
from trbox.market.binance.historical.windows.use_dl_zip_cache import fetch_zip


def test_fetch_zip():
    async def main():
        await fetch_zip('BTCUSDT', '1h', '2022-01-01', '2023-01-31')
    start_time = time.time()
    asyncio.run(main())
    end_time = time.time()
    Log.warning(f'time delta : {end_time-start_time}')
    # time
    # run: await fetch_zip('BTCUSDT', '1h', '2023-01-01', '2023-03-31')
    #   sync: ~0.1368s (cached)
    #   async: ~0.17 (cached)
    # run: await fetch_zip('BTCUSDT', '1h', '2022-01-01', '2023-01-31')
    #   sync: ~1.44s (cached)
    #   async: ~1.95s (cached)
    # conclusion: sync open is slightly faster than async
