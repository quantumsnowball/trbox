import asyncio
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import aiohttp
import aiosqlite
from pandas import date_range

from trbox.market.binance.historical.windows import (ARCHIVE_BASE, CACHE_DIR,
                                                     RAW_COLUMNS, DataType,
                                                     Freq, MarketType,
                                                     UpdateFreq)


async def fetch_sqlite(symbol: str,
                       freq: Freq,
                       start: str,
                       end: str,
                       *,
                       market_type: MarketType = 'spot',
                       update_freq: UpdateFreq = 'daily',
                       data_type: DataType = 'klines',):

    dates = [str(d.date()) for d in date_range(start, end, freq='D')]
    cache_dir = f'{CACHE_DIR}/binance/historical/windows/{market_type}/{update_freq}/{data_type}/{symbol}/{freq}'
    cache_url = f'{cache_dir}/db.sqlite'
    Path(cache_dir).mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(cache_url) as db:
        # assert the table exists
        await db.execute(f"CREATE TABLE IF NOT EXISTS ohlcv({','.join(['Source', *RAW_COLUMNS])})")
        # check what source is already cached
        cursor = await db.execute('SELECT Source FROM ohlcv')
        sources = await cursor.fetchall()
        cursor = await db.execute('PRAGMA table_info(ohlcv)')
        columns = cursor.fetchall()
        # download and cache the missing source
        missing = [date for date in dates if date not in list(sources)]
        if len(missing) > 0:
            async with aiohttp.ClientSession() as session:
                async def download(date) -> None:
                    download_path = f'{ARCHIVE_BASE}/{market_type}/{update_freq}/{data_type}/{symbol}/{freq}'
                    download_fname = f'{symbol}-{freq}-{date}'
                    download_url = f'{download_path}/{download_fname}.zip'
                    async with session.get(download_url) as res:
                        assert res.status == 200
                        print(f'downloaded: {download_url}')
                        zipped = ZipFile(BytesIO(await res.content.read()))
                        unzipped = zipped.open(f'{download_fname}.csv').read()
                        csv = unzipped.decode()
                        entries = [tuple((date, *(v for v in l.split(','))))
                                   for l in csv.split('\n')]
                        await db.executemany('INSERT INTO ohlcv VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', entries)
                        await db.commit()

                await asyncio.gather(*[download(missed) for missed in missing])

        # read the requested data
        cursor = await cursor.execute('SELECT * FROM ohlcv')
        selected = await cursor.fetchall()
        print(selected)


if __name__ == '__main__':
    async def main():
        await fetch_sqlite('BTCUSDT', '1h', '2023-01-01', '2023-01-31')
    asyncio.run(main())
