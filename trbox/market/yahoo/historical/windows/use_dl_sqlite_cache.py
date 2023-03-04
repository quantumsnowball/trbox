from io import BytesIO
from pathlib import Path

import aiohttp
import aiosqlite
from pandas import (DataFrame, Timestamp, date_range, read_csv,
                    to_datetime)
from socketio.asyncio_client import asyncio

from trbox.common.constants import OHLCV_INDEX_NAME
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
    dates = [d.timestamp()
             for d in date_range(start, end, freq='D')]
    cache_dir = f'{CACHE_DIR}/yahoo/historical/windows/{symbol}/{freq}'
    cache_url = f'{cache_dir}/db.sqlite'
    Path(cache_dir).mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(cache_url) as db:
        # assert the table exists
        sql_create_table = ('CREATE TABLE IF NOT EXISTS ohlcv('
                            'Timestamp INT PRIMARY KEY, '
                            'Open NUMERIC, '
                            'High NUMERIC, '
                            'Low NUMERIC, '
                            'Close NUMERIC, '
                            'Volume NUMERIC)')
        await db.execute(sql_create_table)
        # download and cache the missing period
        exists = [ts[0]
                  for ts in await db.execute_fetchall('SELECT Timestamp FROM ohlcv')]
        missing = set(dates).difference(set(exists))
        # download and cache the missing source
        if len(missing) > 0:
            async with aiohttp.ClientSession() as session:
                missing_start = int(min(missing))
                missing_end = int(max(missing)) + 60*60*24

                async def download() -> DataFrame:
                    base = 'https://query1.finance.yahoo.com/v7/finance/download'
                    other_params = 'interval=1d&events=history&includeAdjustedClose=true'
                    download_url = f'{base}/{symbol}?period1={missing_start}&period2={missing_end}&{other_params}'
                    async with session.get(download_url) as res:
                        assert res.status == 200
                        csv = await res.content.read()
                        df = read_csv(BytesIO(csv))
                        df = df.set_index('Date')
                        df.index = to_datetime(df.index.values)
                        df = df.drop('Close', axis=1)
                        df = df.rename(columns={'Adj Close': 'Close'})
                        return df
                downloaded = await download()
                print(f'downloaded ohlcv, symbol="{symbol}", shape={downloaded.shape}',
                      flush=True)
                downloaded_tuples = list(downloaded.itertuples(index=True))
                entries = [tuple((int(t[0].timestamp()), *t[1:]))
                           for t in downloaded_tuples]
                await db.executemany('REPLACE INTO ohlcv VALUES(?, ?, ?, ?, ?, ?)', entries)
                await db.commit()
        # read the requested data
        sql_select = ('SELECT Timestamp,Open,High,Low,Close,Volume '
                      'FROM ohlcv WHERE '
                      f"Timestamp BETWEEN {start_.timestamp()} AND {end_.timestamp()}")
        data = await db.execute_fetchall(sql_select)
        df = DataFrame(
            data, columns='Timestamp,Open,High,Low,Close,Volume'.split(','))
        df = df.rename(columns={'Timestamp': OHLCV_INDEX_NAME})
        df = df.set_index(OHLCV_INDEX_NAME)
        df.index = to_datetime(df.index.values, unit='s')
        df.index.name = OHLCV_INDEX_NAME
        df = df.astype('float')
        df = df.sort_index()
        return df


if __name__ == '__main__':
    async def main() -> None:
        df = await fetch_sqlite('BTC-USD', '1d', '2021-01-15', '2023-01-31')
        print(df)
    asyncio.run(main())
