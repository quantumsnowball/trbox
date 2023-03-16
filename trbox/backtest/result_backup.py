import json
import shutil
import sqlite3
from dataclasses import dataclass
from inspect import currentframe
from pathlib import Path
from sqlite3 import Connection

from pandas import DataFrame, Series, concat

from trbox.common.logger import Log
from trbox.common.utils import cln, localnow
from trbox.portfolio import Portfolio
from trbox.portfolio.stats import StatsDict
from trbox.strategy.mark import Mark


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
    def marks(self) -> dict[str, Mark]:
        return {p.strategy.name: p.strategy.mark for p in self._portfolios}

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
        def save_meta(db: Connection, script_path: Path, timestamp: str, params: dict[str, str]) -> None:
            db.execute('CREATE TABLE IF NOT EXISTS meta(json TEXT)')
            data = json.dumps(dict(
                timestamp=timestamp,
                source=Path(script_path).name,
                params=params,
                strategies=[s.strategy.name for s in self._portfolios],
                marks=sum([len(s.strategy.mark) for s in self._portfolios]),
            ), indent=4)
            db.execute('REPLACE INTO meta VALUES(?)', (data,))
            db.commit()
            print(f'INSERTED: meta', flush=True)

        def save_source(script_path: Path, target_dir: Path) -> None:
            save_path = Path(target_dir, 'source.py')
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
            df = concat(tuple(self.equity.values()), axis=1)
            df.columns = tuple(self.equity.keys())
            df.to_sql('equity', db)
            print(f'INSERTED: equity', flush=True)

        def save_marks(db: Connection) -> None:
            sr = concat([m.series for m in self.marks.values()],
                        keys=self.marks.keys(),
                        names=['strategy',])
            sr.to_sql('marks', db)
            print(f'INSERTED: marks', flush=True)

        try:
            # prepare caller info
            frame = currentframe()
            caller_frame = frame.f_back if frame else None
            globals = caller_frame.f_globals if caller_frame else None
            script_path = Path(globals['__file__']) if globals else Path()
            caller_consts = {k: str(v) for k, v in globals.items()
                             if k.isupper()} if globals else {}
            # prepare directory
            base_dir = Path(script_path).parent.relative_to(Path.cwd())
            timestamp = localnow().isoformat().replace(':', '.')
            target_dir = Path(base_dir, f'.result_{timestamp}')
            target_dir.mkdir(parents=True)
            # save
            save_source(script_path, target_dir)
            db_path = f'{target_dir}/db.sqlite'
            with sqlite3.connect(db_path) as db:
                save_meta(db, script_path, timestamp, caller_consts)
                save_metrics(db)
                save_stats(db)
                save_trades(db)
                save_equity(db)
                save_marks(db)

        except Exception as e:
            Log.exception(e)
