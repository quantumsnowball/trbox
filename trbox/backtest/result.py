import json
import os
import shutil
from dataclasses import dataclass
from inspect import currentframe

from pandas import DataFrame, Series, Timestamp, concat

from trbox.common.logger import Log
from trbox.common.utils import cln
from trbox.portfolio import Portfolio


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
    def stats(self) -> DataFrame:
        return concat([p.stats.df for p in self._portfolios], axis=0)

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
        def save_meta(script_path: str, target_dir: str, timestamp: str, params: dict[str, str]) -> None:
            save_path = f'{target_dir}/meta.json'
            json.dump(dict(
                timestamp=timestamp,
                source=os.path.basename(script_path),
                params=params,
                strategies=[s.strategy.name for s in self._portfolios],
            ), open(save_path, 'w'), indent=4)
            print(f'SAVED: {save_path}', flush=True)

        def save_source(script_path: str, target_dir: str) -> None:
            save_path = f'{target_dir}/source.py'
            shutil.copy(script_path, save_path)
            print(f'SAVED: {save_path}', flush=True)

        def save_metrics(target_dir: str) -> None:
            save_path = f'{ target_dir }/metrics.pkl'
            self.metrics.to_pickle(save_path)
            print(f'SAVED: {save_path}', flush=True)

        def save_stats(target_dir: str) -> None:
            save_path = f'{ target_dir }/stats.pkl'
            self.stats.to_pickle(save_path)
            print(f'SAVED: {save_path}', flush=True)

        def save_equity(target_dir: str) -> None:
            save_path = f'{ target_dir }/equity.pkl'
            df = concat(tuple(self.equity.values()), axis=1)
            df.columns = tuple(self.equity.keys())
            df.to_pickle(save_path)
            print(f'SAVED: {save_path}', flush=True)

        def save_trades(target_dir: str) -> None:
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
            timestamp = Timestamp.now().isoformat().replace(':', '.')
            target_dir = f'{base_dir}/.result_{timestamp}'
            os.makedirs(target_dir)
            # save
            save_meta(script_path, target_dir, timestamp, caller_consts)
            save_source(script_path, target_dir)
            save_metrics(target_dir)
            save_equity(target_dir)
            save_trades(target_dir)
            save_stats(target_dir)
        except Exception as e:
            Log.exception(e)
