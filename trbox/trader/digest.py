from dataclasses import dataclass

from pandas import DataFrame, Series

from trbox.portfolio.stats import StatsDict
from trbox.strategy.mark import Mark


@dataclass
class Digest:
    '''
    This class must be picklable in order to send through multi processes
    '''
    name: str
    metrics: DataFrame
    stats: StatsDict
    equity: Series
    mark: Mark
    trades: DataFrame
