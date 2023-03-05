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
    dates = [d.timestamp()
             for d in date_range(start_, end_, freq='D')]
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
                missing_end = int(max(missing))
                for _ in range(retry):
                    try:
                        # download
                        async def download() -> DataFrame:
                            base = 'https://query1.finance.yahoo.com/v7/finance/download'
                            other_params = f'interval={freq}&events=history&includeAdjustedClose=true'
                            download_url = f'{base}/{quote(symbol)}?period1={missing_start}&period2={missing_end}&{other_params}'
                            async with session.get(download_url,
                                                   timeout=aiohttp.ClientTimeout(timeout)) as res:
                                assert res.status == 200
                                csv = await res.content.read()
                                df = read_csv(BytesIO(csv))
                                df = df.set_index('Date')
                                df.index = to_datetime(df.index.values)
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
                        # extract
                        downloaded_tuples = list(
                            downloaded.itertuples(index=True))
                        entries = [tuple((int(t[0].timestamp()), *t[1:]))
                                   for t in downloaded_tuples]
                        # insert
                        await db.executemany('REPLACE INTO ohlcv VALUES(?, ?, ?, ?, ?, ?)', entries)
                        await db.commit()
                        # successfully done
                        break
                    except Exception as e:
                        # will retry download and insert on Exception
                        Log.exception(e)
                else:
                    # will allow return even if download failed
                    Log.critical(f'Failed to download from Yahoo Finance')
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
        # verify dataframe integrity
        assert to_datetime(start) <= df.index[0] <= \
            to_datetime(start) + Timedelta(days=ERROR)
        assert to_datetime(end) - Timedelta(days=ERROR) <= \
            df.index[-1] <= to_datetime(end)
        gaps = Series(df.index, index=df.index).diff().dropna()
        assert gaps.max().days <= MAX_GAP, 'Gaps exists in the dataframe'
        # done
        return df


if __name__ == '__main__':
    async def main() -> None:
        df = await fetch_sqlite('BTC-USD', '1d', '2021-01-15', '2021-01-31')
        print(df)
    asyncio.run(main())
