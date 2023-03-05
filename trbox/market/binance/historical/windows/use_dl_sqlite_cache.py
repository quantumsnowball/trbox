import asyncio
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import aiohttp
import aiosqlite
from pandas import DataFrame, Timestamp, date_range, to_datetime

from trbox.common.constants import OHLCV_INDEX_NAME
from trbox.common.logger import Log
from trbox.common.utils import utcnow
from trbox.market.binance.historical.windows.constants import (ARCHIVE_BASE,
                                                               CACHE_DIR,
                                                               DataType, Freq,
                                                               MarketType,
                                                               UpdateFreq)


async def fetch_sqlite(symbol: str,
                       freq: Freq,
                       start: str | Timestamp,
                       end: str | Timestamp,
                       *,
                       market_type: MarketType = 'spot',
                       update_freq: UpdateFreq = 'daily',
                       data_type: DataType = 'klines',
                       retry: int = 10,
                       timeout: int = 5) -> DataFrame:
    # create db dir if not exist
    start_: Timestamp = to_datetime(start)
    end_: Timestamp = to_datetime(end)
    assert start_ < end_, 'Start date must be before end date'
    assert end_ <= utcnow(), 'Future timestamp not allowed'
    dates = [str(d.date())
             for d in date_range(start_, end_, freq='D')]
    cache_dir = f'{CACHE_DIR}/binance/historical/windows/{market_type}/{update_freq}/{data_type}/{symbol}/{freq}'
    cache_url = f'{cache_dir}/db.sqlite'
    Path(cache_dir).mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(cache_url) as db:
        # assert the table exists
        sql_create_table = ('CREATE TABLE IF NOT EXISTS ohlcv('
                            'Source TEXT, '
                            'Open NUMERIC, '
                            'High NUMERIC, '
                            'Low NUMERIC, '
                            'Close NUMERIC, '
                            'Volume NUMERIC, '
                            'CloseTime INT PRIMARY KEY)')
        await db.execute(sql_create_table)
        # check what source is already cached
        exists = [r[0]
                  for r in await db.execute_fetchall('SELECT Source FROM ohlcv')]
        missing = set(dates).difference(set(exists))
        # download and cache the missing source
        if len(missing) > 0:
            async with aiohttp.ClientSession() as session:
                async def download(date: str) -> None:
                    download_path = f'{ARCHIVE_BASE}/{market_type}/{update_freq}/{data_type}/{symbol}/{freq}'
                    download_fname = f'{symbol}-{freq}-{date}'
                    download_url = f'{download_path}/{download_fname}.zip'
                    for _ in range(retry):
                        try:
                            async with session.get(download_url,
                                                   timeout=aiohttp.ClientTimeout(timeout)) as res:
                                # download
                                assert res.status == 200
                                print(f'downloaded: {download_url}')
                                # unzip
                                zipped = ZipFile(BytesIO(await res.content.read()))
                                unzipped = zipped.open(
                                    f'{download_fname}.csv').read()
                                csv = unzipped.decode()
                                # insert
                                entries = [tuple((date, *([v for v in l.split(',')][1:7])))
                                           for l in csv.split('\n')
                                           if len(l) > 0]
                                await db.executemany('REPLACE INTO ohlcv VALUES(?, ?, ?, ?, ?, ?, ?)', entries)
                                await db.commit()
                                # successfully done
                                break
                        except Exception as e:
                            # will retry download and insert on Exception
                            Log.exception(e)
                    else:
                        # will allow return even if download failed
                        Log.critical(f'Failed to download from Binance')
                # download all missed data async
                await asyncio.gather(*[download(missed) for missed in missing])
        # read the requested data
        sql_select = ('SELECT Open,High,Low,Close,Volume,CloseTime '
                      'FROM ohlcv WHERE '
                      f'CloseTime >= {start_.timestamp()*1e3} AND '
                      f'CloseTime <= {end_.timestamp()*1e3};')
        data = await db.execute_fetchall(sql_select)
        df = DataFrame(
            data, columns='Open,High,Low,Close,Volume,CloseTime'.split(','))
        df = df.rename(columns={'CloseTime': OHLCV_INDEX_NAME})
        df = df.set_index(OHLCV_INDEX_NAME)
        df.index = to_datetime(df.index.values, unit='ms').round('S')
        df.index.name = OHLCV_INDEX_NAME
        df = df.astype('float')
        df = df.sort_index()
        return df


if __name__ == '__main__':
    async def main() -> None:
        df = await fetch_sqlite('BTCUSDT', '1m', '2023-03-15', '2023-03-08')
        print(df)
    asyncio.run(main())
