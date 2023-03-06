from __future__ import annotations

from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING, Iterable, Self

from typing_extensions import override

from trbox.backtest.monitor import monitor
from trbox.backtest.result import Result
from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.common.utils import cln
from trbox.event.monitor import EnableOutput

if TYPE_CHECKING:
    from trbox.trader import Runner, Trader


class BatchRunner(ABC):
    '''
    The base class for handling a collection of Runners
    '''

    @abstractmethod
    def __init__(self) -> None:
        self._runners: Iterable[Runner]

    def _run_sync(self) -> None:
        for id, runner in enumerate(self._runners):
            Log.info(Memo('started', cln(runner), id=id)
                     .by(self).tag('runner', 'started'))
            runner.run()
            Log.info(Memo('finished', cln(runner), id=id)
                     .by(self).tag('runner', 'finished'))
        Log.info(Memo('finished', cln(self))
                 .by(self).tag('batch', 'finished'))

    def _run_async(self) -> None:
        with ThreadPoolExecutor(thread_name_prefix='BacktestPool') as executor:
            Log.info(Memo('started', cln(executor))
                     .by(self).tag('pool', 'started'))
            futures = [executor.submit(r.run) for r in self._runners]
            for future in futures:
                future.result()
            # block here until all future has resolved
            Log.info(Memo('finished', cln(executor))
                     .by(self).tag('pool', 'finished'))

    @abstractmethod
    def run(self, *, parallel: bool = False) -> Self:
        pass


class Backtest(BatchRunner):
    '''
    Should accept a list of Trader and run them.
    Only accept Trader in backtest mode.
    '''

    def __init__(self,
                 *traders: Trader,
                 progress: int | None = 5) -> None:
        super().__init__()
        for trader in traders:
            assert trader.backtesting
        self._runners: tuple[Trader, ...] = traders
        self._portfolios = [t.portfolio for t in traders]
        if progress is not None:
            monitor.put(EnableOutput(display=print,
                                     step=progress,
                                     count=len(traders)))

    @property
    def traders(self) -> tuple[Trader, ...]:
        return self._runners

    @property
    def result(self) -> Result:
        return Result(*self._portfolios)

    @override
    def run(self, *, parallel: bool = True) -> Self:
        self._run_async() if parallel else self._run_sync()
        return self
