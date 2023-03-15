import asyncio
import sqlite3
from pathlib import Path
from pprint import pformat
from typing import Any

import pandas as pd
from pandas import DataFrame, Timestamp

from trbox.common.constants import OHLCV_COLUMN_NAMES


def verify_ohlcv(ohlcv: DataFrame) -> DataFrame:
    # ensure the window has valid values
    assert isinstance(ohlcv, DataFrame)
    assert ohlcv.index.name == 'Date'
    assert (ohlcv.columns == OHLCV_COLUMN_NAMES).all()
    assert not ohlcv.isnull().any().any()
    assert not ohlcv.isna().any().any()
    return ohlcv


def trim_ohlcv_by_range_length(
        df: DataFrame,
        start: Timestamp,
        end: Timestamp | None,
        length: int) -> DataFrame:
    '''
    given a dataframe, start, end and length, check the validity of all
    inputs, trim the dataframe correctly to be used in datasource generator,
    '''
    # check if the config make sense
    assert len(df) > length
    if start and end:
        assert start < end
    # find the correct trim_from date
    trim_from = df.loc[:start].iloc[-length:].index[0]
    # trim_to date is the end date
    trim_to = end
    # applyy trim and return df
    df = df.loc[trim_from:trim_to]
    return df


def cln(obj: Any) -> str:
    '''
    print class name for any object
    '''
    try:
        name = obj.__class__.__name__
        if isinstance(name, str):
            return name
        # try the best to resolve a name
        return str(obj)
    except Exception:
        # return a default str
        return str(obj)


def ppf(obj: Any) -> str:
    try:
        return pformat(obj)
    except Exception:
        return str(obj)


def localnow() -> Timestamp:
    return Timestamp.now()


def localnow_string() -> str:
    return localnow().isoformat().replace('T', ' ')[:-7]


def utcnow() -> Timestamp:
    return Timestamp.utcnow().tz_localize(None)


async def read_sql_async(sql: str,
                         db: Path,
                         *args: Any,
                         **kwargs: Any) -> DataFrame:
    def read_sql_sync():
        with sqlite3.connect(db) as con:
            df = pd.read_sql(sql, con, *args, **kwargs)
            return df
    return await asyncio.to_thread(read_sql_sync)


async def to_sql_async(df: DataFrame,
                       name: str,
                       db: Path,
                       *args: Any,
                       **kwargs: Any) -> None:
    def to_sql_sync():
        with sqlite3.connect(db) as con:
            df.to_sql(name, con, *args, **kwargs)
    await asyncio.to_thread(to_sql_sync)
