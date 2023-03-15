import asyncio
import sqlite3
from io import BytesIO
from pathlib import Path
from sqlite3 import OperationalError
from urllib.parse import quote

import aiohttp
import aiosqlite
from pandas import (DataFrame, Series, Timedelta, Timestamp, date_range,
                    read_csv, to_datetime)

from trbox.common.constants import OHLCV_INDEX_NAME
from trbox.common.logger import Log
from trbox.common.utils import read_sql_async, utcnow
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
    cache_dir = Path(f'{CACHE_DIR}/yahoo/historical/windows/{symbol}/{freq}')
    cache_url = Path(f'{cache_dir}/db.sqlite')
    cache_dir.mkdir(parents=True, exist_ok=True)
    # decide if the data exists and up to date

    async def data_is_up_to_date() -> bool:
        try:
            async with aiosqlite.connect(cache_url) as db:
                meta = tuple(await db.execute_fetchall('SELECT * from meta'))
                last_updated, timestamp_first, timestamp_last = meta[0]
                # full coverage
                if start_.timestamp() > timestamp_first and end_.timestamp() < timestamp_last:
                    return True
                # data is fresh within 1d
                if utcnow().timestamp() < last_updated + 86400:
                    return True
        except (KeyError, OperationalError):
            # meta data not available or meta table not exists
            pass
        # default
        return False
    # if data is outdated download and replace the data
    if not await data_is_up_to_date():
        for i in range(retry):
            try:
                # download max length data

                async def download() -> DataFrame:
                    base = 'https://query1.finance.yahoo.com/v7/finance/download'
                    other_params = f'interval={freq}&events=history&includeAdjustedClose=true'
                    download_url = f'{base}/{quote(symbol)}?period1=0&period2={int(utcnow().timestamp())}&{other_params}'
                    async with aiohttp.ClientSession() as session:
                        async with session.get(download_url,
                                               timeout=aiohttp.ClientTimeout(timeout)) as res:
                            assert res.status == 200
                            csv = await res.content.read()
                            df = read_csv(BytesIO(csv))
                            df['Date'] = to_datetime(
                                df['Date']).astype(int) // 1e9
                            df = df.rename(columns={'Date': 'Timestamp'})
                            # adjust
                            adj_ratio = df['Adj Close']/df['Close']
                            df['Open'] *= adj_ratio
                            df['High'] *= adj_ratio
                            df['Low'] *= adj_ratio
                            df['Volume'] /= adj_ratio
                            # ensure min max
                            df['High'] = df[['Open', 'High', 'Close']].apply(max,
                                                                             axis=1)
                            df['Low'] = df[['Open', 'Low', 'Close']].apply(min,
                                                                           axis=1)
                            # trim and rename
                            df = df.drop('Close', axis=1)
                            df = df.rename(columns={'Adj Close': 'Close'})
                            # clean
                            df = df.dropna(how='any', axis=0)
                            # done
                            return df
                downloaded = await download()
                print(f'downloaded ohlcv, symbol="{symbol}", shape={downloaded.shape}',
                      flush=True)
                # purge the database
                async with aiosqlite.connect(cache_url) as db:
                    await db.execute('DROP TABLE IF EXISTS ohlcv')
                    await db.execute('DROP TABLE IF EXISTS meta')
                # insert to ohlcv table
                with sqlite3.connect(cache_url) as db:
                    downloaded.to_sql('ohlcv', db, index=False)
                # write meta data
                meta = DataFrame(dict(last_updated=utcnow().timestamp(),
                                      start=downloaded['Timestamp'].iloc[0],
                                      end=downloaded['Timestamp'].iloc[-1]), index=[0])
                with sqlite3.connect(cache_url) as db:
                    meta.to_sql('meta', db, index=False)
                # successfully done
                break
            except Exception:
                # will retry download and insert on Exception
                Log.info(f'Download failed, retrying {i+1}/{retry}')
        else:
            # will allow return even if download failed
            Log.info(f'Failed to download from Yahoo Finance')
    # read the requested data and return
    sql_select = ('SELECT Timestamp,Open,High,Low,Close,Volume '
                  'FROM ohlcv WHERE '
                  f"Timestamp BETWEEN {start_.timestamp()} AND {end_.timestamp()}")
    df = await read_sql_async(sql_select, cache_url)
    df = df.rename(columns={'Timestamp': OHLCV_INDEX_NAME})
    df = df.set_index(OHLCV_INDEX_NAME)
    df.index = to_datetime(df.index.values, unit='s')
    df.index.name = OHLCV_INDEX_NAME
    df = df.astype('float')
    df = df.sort_index()
    # done
    return df


if __name__ == '__main__':
    async def main() -> None:
        df = await fetch_sqlite('SPY', '1d', '2021-01-15', '2021-01-31')
        print(df.shape)
        print(df.columns)
    asyncio.run(main())
