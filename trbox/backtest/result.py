import json
import os
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
        try:
            # prepare directory
            base_dir = os.path.relpath(os.path.dirname(script_path))
            timestamp = Timestamp.now().isoformat().replace(':', '.')
            target_dir = f'{base_dir}/.result_{timestamp}'
            os.makedirs(target_dir)
            # save metrics
            fn_metrics = f'{ target_dir }/metrics.pkl'
            self.metrics.to_pickle(fn_metrics)
            print(f'SAVED: {fn_metrics}', flush=True)
            # save equity
            fn_equity = f'{ target_dir }/equity.pkl'
            concat(list(self.equity.values()), axis=1).to_pickle(fn_equity)
            print(f'SAVED: {fn_equity}', flush=True)
        except Exception as e:
            Log.exception(e)
