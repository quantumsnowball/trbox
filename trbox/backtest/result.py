import json
import os
import pickle
import shutil
import sqlite3
from dataclasses import dataclass
from inspect import currentframe
from sqlite3 import Connection

from pandas import DataFrame, Series, Timestamp, concat

from trbox.common.logger import Log
from trbox.common.utils import cln, localnow
from trbox.portfolio import Portfolio
from trbox.portfolio.stats import StatsDict


@dataclass
class Result:
    desc: str = 'A collection of all trader dashboard with summary'

    def __init__(self, *portfolios: Portfolio) -> None:
        self._portfolios = portfolios

    def __str__(self) -> str:
        return f'{cln(self)}({self.desc})'

    #
    # analysis
    #

    @property
    def metrics(self) -> DataFrame:
        return concat([p.metrics.df for p in self._portfolios], axis=0)

    @property
    def stats(self) -> dict[str, StatsDict]:
        return {p.strategy.name: p.stats.dict for p in self._portfolios}

    @property
    def equity(self) -> dict[str, Series]:
        return {p.strategy.name: p.dashboard.equity for p in self._portfolios}

    @property
    def trades(self) -> dict[str, DataFrame]:
        return {p.strategy.name: p.dashboard.trades for p in self._portfolios}
    #
    # presenting
    #

    def plot(self) -> None:
        # TODO combine all traders and plot at one single chart
        ...

    #
    # save
    #
    def save(self) -> None:
        def save_meta(db: Connection, script_path: str, timestamp: str, params: dict[str, str]) -> None:
            db.execute('CREATE TABLE IF NOT EXISTS meta(json TEXT)')
            data = json.dumps(dict(
                timestamp=timestamp,
                source=os.path.basename(script_path),
                params=params,
                strategies=[s.strategy.name for s in self._portfolios],
            ), indent=4)
            db.execute('REPLACE INTO meta VALUES(?)', (data,))
            db.commit()
            print(f'INSERTED: meta', flush=True)

        def save_source(script_path: str, target_dir: str) -> None:
            save_path = f'{target_dir}/source.py'
            shutil.copy(script_path, save_path)
            print(f'SAVED: {save_path}', flush=True)

        def save_metrics(db: Connection) -> None:
            self.metrics.to_sql('metrics', db)
            db.commit()
            print(f'INSERTED: metrics', flush=True)

        def save_stats(db: Connection) -> None:
            db.execute(
                'CREATE TABLE IF NOT EXISTS stats(name TEXT, json TEXT)')
            data = [(name, json.dumps(stat, indent=4))
                    for name, stat in self.stats.items()]
            db.executemany('replace into stats values(?,?)', data)
            db.commit()
            print(f'INSERTED: stats', flush=True)

        def save_trades(db: Connection) -> None:
            df = concat(tuple(self.trades.values()),
                        keys=tuple(self.trades.keys()),
                        names=('Strategy', 'Date'),
                        axis=0,)
            df.to_sql('trades', db)
            print(f'INSERTED: trades', flush=True)

        def save_equity(db: Connection) -> None:
            # save_path = f'{ target_dir }/equity.pkl'
            # df.to_pickle(save_path)
            df = concat(tuple(self.equity.values()), axis=1)
            df.columns = tuple(self.equity.keys())
            df.to_sql('equity', db)
            print(f'INSERTED: equity', flush=True)

        # deprecated

        def _save_meta(script_path: str, target_dir: str, timestamp: str, params: dict[str, str]) -> None:
            save_path = f'{target_dir}/meta.json'
            json.dump(dict(
                timestamp=timestamp,
                source=os.path.basename(script_path),
                params=params,
                strategies=[s.strategy.name for s in self._portfolios],
            ), open(save_path, 'w'), indent=4)
            print(f'SAVED: {save_path}', flush=True)

        def _save_metrics(target_dir: str) -> None:
            save_path = f'{ target_dir }/metrics.pkl'
            self.metrics.to_pickle(save_path)
            print(f'SAVED: {save_path}', flush=True)

        def _save_stats(target_dir: str) -> None:
            save_path = f'{ target_dir }/stats.pkl'
            with open(save_path, 'wb') as f:
                pickle.dump(self.stats, f)
            print(f'SAVED: {save_path}', flush=True)

        def _save_equity(target_dir: str) -> None:
            save_path = f'{ target_dir }/equity.pkl'
            df = concat(tuple(self.equity.values()), axis=1)
            df.columns = tuple(self.equity.keys())
            df.to_pickle(save_path)
            print(f'SAVED: {save_path}', flush=True)

        def _save_trades(target_dir: str) -> None:
            save_path = f'{ target_dir }/trades.pkl'
            df = concat(tuple(self.trades.values()),
                        keys=tuple(self.trades.keys()),
                        names=('Strategy', 'Date'),
                        axis=0,)
            df.to_pickle(save_path)
            print(f'SAVED: {save_path}', flush=True)

        try:
            # prepare caller info
            frame = currentframe()
            caller_frame = frame.f_back if frame else None
            globals = caller_frame.f_globals if caller_frame else None
            script_path = str(globals['__file__']) if globals else ''
            caller_consts = {k: str(v) for k, v in globals.items()
                             if k.isupper()} if globals else {}
            # prepare directory
            base_dir = os.path.relpath(os.path.dirname(script_path))
            timestamp = localnow().isoformat().replace(':', '.')
            target_dir = f'{base_dir}/.result_{timestamp}'
            os.makedirs(target_dir)
            # save
            # _save_meta(script_path, target_dir, timestamp, caller_consts)
            # save_source(script_path, target_dir)
            # _save_metrics(target_dir)
            _save_equity(target_dir)
            # _save_trades(target_dir)
            # _save_stats(target_dir)
            # save sqlite
            save_source(script_path, target_dir)
            db_path = f'{target_dir}/db.sqlite'
            with sqlite3.connect(db_path) as db:
                save_meta(db, script_path, timestamp, caller_consts)
                save_metrics(db)
                save_stats(db)
                save_trades(db)
                save_equity(db)

        except Exception as e:
            Log.exception(e)
