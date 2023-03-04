
from pathlib import Path

import aiosqlite
import yfinance as yf
from pandas import DataFrame, Timedelta, Timestamp, date_range, to_datetime
from socketio.asyncio_client import asyncio

from trbox.common.constants import OHLCV_COLUMN_NAMES
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
                            'Date TEXT PRIMARY KEY, '
                            'Open NUMERIC, '
                            'High NUMERIC, '
                            'Low NUMERIC, '
                            'Close NUMERIC, '
                            'Volume NUMERIC)')
        await db.execute(sql_create_table)
        #
        tmp = await db.execute_fetchall('PRAGMA table_info(ohlcv);')
        print(tmp)
        # download and cache the missing period
        sources = [str(to_datetime(r[0]).date())
                   for r in await db.execute_fetchall('SELECT Date FROM ohlcv')]
        missing = set(dates).difference(set(sources))
        # download and cache the missing source
        if len(missing) > 0:
            missing_start = min(missing)
            missing_end = str(to_datetime(
                max(missing)).date() + Timedelta(days=1))

            def download(symbol: str) -> DataFrame:
                ticker = yf.Ticker(symbol)
                df: DataFrame = ticker.history(start=missing_start,
                                               end=missing_end,
                                               interval=freq)
                df = DataFrame(df.tz_localize(None))
                df = df[OHLCV_COLUMN_NAMES]
                return df
            df = download(symbol)
            print(f'downloaded ohlcv, symbol="{symbol}", shape={df.shape}',
                  flush=True)
            df_tuples = list(df.itertuples(index=True))
            entries = [tuple((t[0].isoformat(), *t[1:])) for t in df_tuples]
            await db.executemany('REPLACE INTO ohlcv VALUES(?, ?, ?, ?, ?, ?)', entries)
            await db.commit()
        # read the requested data
        sql_select = ('SELECT Date,Open,High,Low,Close,Volume '
                      'FROM ohlcv WHERE '
                      f"Date BETWEEN '{start_.isoformat()}' AND '{end_.isoformat()}'")
        data = await db.execute_fetchall(sql_select)
        print(data)


if __name__ == '__main__':
    async def main() -> None:
        df = await fetch_sqlite('BTC-USD', '1d', '2023-01-15', '2023-01-31')
        print(df)
    asyncio.run(main())
