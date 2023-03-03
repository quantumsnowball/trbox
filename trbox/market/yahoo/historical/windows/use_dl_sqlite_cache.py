
from pathlib import Path

import aiosqlite
from pandas import DataFrame, Timestamp, date_range, to_datetime
from socketio.asyncio_client import asyncio

from trbox.market.yahoo.historical.windows.constants import CACHE_DIR, Freq


async def fetch_sqlite(symbol: str,
                       freq: Freq,
                       start: str | Timestamp,
                       end: str | Timestamp,
                       *,
                       retry: int = 10,
                       timeout: int = 5) -> DataFrame:
    # create db if not exist
    start_: Timestamp = to_datetime(start)
    end_: Timestamp = to_datetime(end if end else Timestamp.now())
    dates = [str(d.date())
             for d in date_range(start, end, freq='D')]
    cache_dir = f'{CACHE_DIR}/yahoo/historical/windows/{symbol}/{freq}'
    cache_url = f'{cache_dir}/db.sqlite'
    Path(cache_dir).mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(cache_url) as db:
        # assert the table exists
        sql_create_table = ('CREATE TABLE IF NOT EXISTS ohlcv('
                            'Open NUMERIC, '
                            'High NUMERIC, '
                            'Low NUMERIC, '
                            'Close NUMERIC, '
                            'Volume NUMERIC, '
                            'Date TEXT PRIMARY KEY)')
        await db.execute(sql_create_table)
        #
        tmp = await db.execute_fetchall('PRAGMA table_info(ohlcv);')
        print(tmp)


if __name__ == '__main__':
    async def main() -> None:
        df = await fetch_sqlite('BTC-USD', '1d', '2023-01-15', '2023-01-31')
        print(df)
    asyncio.run(main())
