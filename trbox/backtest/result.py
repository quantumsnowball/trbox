import os
from dataclasses import dataclass
from datetime import datetime
from os.path import isdir

from pandas import DataFrame, Timestamp, concat

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
        try:
            base_dir = os.path.relpath(os.path.dirname(script_path))
            timestamp = Timestamp.now().isoformat().replace(':', '.')
            target_dir = f'{base_dir}/.result_{timestamp}'
            target_filename = f'{ target_dir }/metrics.json'
            os.makedirs(target_dir)
            self.metrics.to_json(target_filename, indent=4)
            print(f'SAVED: {target_filename}', flush=True)
        except Exception as e:
            Log.exception(e)
