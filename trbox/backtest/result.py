import json
import os
import shutil
from dataclasses import dataclass

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
    def equity(self) -> dict[str, Series]:
        return {p.strategy.name: p.dashboard.equity for p in self._portfolios}
    #
    # presenting
    #

    def plot(self) -> None:
        # TODO combine all traders and plot at one single chart
        ...

    #
    # save
    #
    def save(self, script_path: str) -> None:
        def save_meta(target_dir: str, timestamp: str) -> None:
            save_path = f'{target_dir}/meta.json'
            json.dump(dict(
                timestamp=timestamp,
                source=os.path.basename(script_path),
            ), open(save_path, 'w'), indent=4)
            print(f'SAVED: {save_path}', flush=True)

        def save_source(target_dir: str) -> None:
            save_path = f'{target_dir}/source.py'
            shutil.copy(script_path, save_path)
            print(f'SAVED: {save_path}', flush=True)

        def save_metrics(target_dir: str) -> None:
            save_path = f'{ target_dir }/metrics.pkl'
            self.metrics.to_pickle(save_path)
            print(f'SAVED: {save_path}', flush=True)

        def save_equity(target_dir: str) -> None:
            save_path = f'{ target_dir }/equity.pkl'
            df = concat(tuple(self.equity.values()), axis=1)
            df.columns = tuple(self.equity.keys())
            df.to_pickle(save_path)
            print(f'SAVED: {save_path}', flush=True)

        try:
            # prepare directory
            base_dir = os.path.relpath(os.path.dirname(script_path))
            timestamp = Timestamp.now().isoformat().replace(':', '.')
            target_dir = f'{base_dir}/.result_{timestamp}'
            os.makedirs(target_dir)
            # save
            save_meta(target_dir, timestamp)
            save_source(target_dir)
            save_metrics(target_dir)
            save_equity(target_dir)
        except Exception as e:
            Log.exception(e)
