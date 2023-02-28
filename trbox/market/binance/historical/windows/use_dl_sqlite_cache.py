import asyncio
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import aiohttp
import aiosqlite
from pandas import DataFrame, date_range, to_datetime

from trbox.common.constants import OHLCV_INDEX_NAME
from trbox.market.binance.historical.windows import (ARCHIVE_BASE, CACHE_DIR,
                                                     RAW_COLUMNS,
                                                     SELECTED_COLUMNS,
                                                     DataType, Freq,
                                                     MarketType, UpdateFreq)


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
        sources = [r[0] for r in await cursor.fetchall()]
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
                                   for l in csv.split('\n')
                                   if len(l) > 0]
                        await db.executemany('REPLACE INTO ohlcv VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', entries)
                        await db.commit()

                await asyncio.gather(*[download(missed) for missed in missing])

        # read the requested data
        cursor = await cursor.execute(f"SELECT {','.join(SELECTED_COLUMNS)} FROM ohlcv")
        data = await cursor.fetchall()
        df = DataFrame(data, columns=SELECTED_COLUMNS)
        df = df.rename(columns={'CloseTime': OHLCV_INDEX_NAME})
        df = df.set_index(OHLCV_INDEX_NAME)
        df.index = to_datetime(df.index.values, unit='ms').round('S')
        df = df.sort_index()
        return df


if __name__ == '__main__':
    async def main():
        df = await fetch_sqlite('BTCUSDT', '1h', '2023-01-01', '2023-01-31')
        print(df)
    asyncio.run(main())
