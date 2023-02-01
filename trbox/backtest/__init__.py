from abc import ABC, abstractmethod
from typing import Any, Iterable
from trbox.common.logger.parser import Log
from trbox.common.utils import cln
from trbox.strategy import Strategy
from trbox.trader import Runner, Trader
from trbox.common.logger import info


class BatchRunner(ABC):
    '''
    The base class for handling a collection of Runners
    '''

    @abstractmethod
    def __init__(self) -> None:
        self._runners: Iterable[Runner]

    def run(self) -> None:
        for id, runner in enumerate(self._runners):
            info(Log('started', cln(runner), id=id)
                 .by(self).tag('runner', 'started'))
            runner.run()
            info(Log('finished', cln(runner), id=id)
                 .by(self).tag('runner', 'finished'))
        info(Log('finished', cln(self))
             .by(self).tag('batch', 'finished'))

    def run_parallel(self) -> None:
        # TODO thread pool to execute all Runner
        pass


class Backtest(BatchRunner):
    '''
    Should accept a list of Trader and run them.
    Only accept Trader in backtest mode.
    '''

    def __init__(self, *traders: Trader) -> None:
        super().__init__()
        for trader in traders:
            assert trader.backtesting
        self._runners = traders
