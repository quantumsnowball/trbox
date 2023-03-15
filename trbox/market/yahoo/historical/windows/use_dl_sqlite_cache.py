import asyncio
from io import BytesIO
from pathlib import Path
from urllib.parse import quote

import aiohttp
import aiosqlite
from pandas import (DataFrame, Series, Timedelta, Timestamp, date_range,
                    read_csv, to_datetime)

from trbox.common.constants import OHLCV_INDEX_NAME
from trbox.common.logger import Log
from trbox.common.utils import utcnow
from trbox.market.yahoo.historical.windows.constants import (CACHE_DIR, ERROR,
                                                             MAX_GAP, Freq)


async def fetch_sqlite(symbol: str,
                       freq: Freq,
                       start: str | Timestamp,
                       end: str | Timestamp,
                       *,
                       retry: int = 10,
                       timeout: int = 5) -> DataFrame:
    # create db if not exist
    start_: Timestamp = to_datetime(start)
    end_: Timestamp = to_datetime(end)
    assert start_ < end_, 'Start date must be before end date'
    assert end_ <= utcnow(), 'Future timestamp not allowed'
    cache_dir = f'{CACHE_DIR}/yahoo/historical/windows/{symbol}/{freq}'
    cache_url = f'{cache_dir}/db.sqlite'
    Path(cache_dir).mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(cache_url) as db:
        # assert the table exists
        sql_create_ohlcv_table = ('CREATE TABLE IF NOT EXISTS ohlcv('
                                  'Timestamp INT PRIMARY KEY, '
                                  'Open NUMERIC, '
                                  'High NUMERIC, '
                                  'Low NUMERIC, '
                                  'Close NUMERIC, '
                                  'Volume NUMERIC)')
        await db.execute(sql_create_ohlcv_table)
        sql_create_meta_table = ('CREATE TABLE IF NOT EXISTS meta('
                                 'last_updated NUMERIC, '
                                 'start NUMERIC, '
                                 'end NUMERIC)')
        await db.execute(sql_create_meta_table)
        # decide if the data exists and up to date

        async def data_is_up_to_date() -> bool:
            meta = tuple(await db.execute_fetchall('SELECT * from meta'))
            if len(meta) == 0:
                return False
            last_updated, timestamp_first, timestamp_last = meta[0]
            print(meta)
            return False
        # if data is outdated download and replace the data
        if not await data_is_up_to_date():
            # purge the database
            # download max length data
            # process and convert the data
            # insert to ohlcv table
            # write meta data
            print('gonna download again')
        # read the requested data and return


if __name__ == '__main__':
    async def main() -> None:
        df = await fetch_sqlite('SPY', '1d', '2021-01-15', '2021-01-31')
        print(df)
    asyncio.run(main())
