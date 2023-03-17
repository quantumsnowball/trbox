from __future__ import annotations

from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Process, Queue
from threading import Thread
from typing import TYPE_CHECKING, Iterable, Literal, Self

from typing_extensions import override

from trbox.backtest.monitor import monitor
from trbox.backtest.result import Result
from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.common.utils import cln
from trbox.event.monitor import EnableOutput
from trbox.event.system import Exit
from trbox.trader.digest import Digest

if TYPE_CHECKING:
    from trbox.trader import Runner, Trader

Mode = Literal['serial', 'thread', 'process']


class BatchRunner(ABC):
    '''
    The base class for handling a collection of Runners
    '''

    @abstractmethod
    def __init__(self) -> None:
        self._runners: Iterable[Runner]
        self._digests: Iterable[Digest]

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

    def _run_multiprocess(self) -> None:
        result_queues: list[Queue[Digest]] = [Queue() for _ in self._runners]
        procs = [Process(target=runner.run, args=(queue,))
                 for runner, queue in zip(self._runners, result_queues)]
        # start
        for p in procs:
            p.start()
        Log.info(Memo('started', n_procs=len(procs))
                 .by(self).tag('pool', 'started'))
        # block here until all process finished
        # get back all trader result digest
        self._digests = tuple(queue.get()
                              for queue in result_queues)
        # join and exit
        for p in procs:
            p.join()
        Log.info(Memo('finished', n_procs=len(procs))
                 .by(self).tag('pool', 'finished'))

    @abstractmethod
    def run(self, *, mode: Mode = 'process') -> Self:
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
            monitor.put(EnableOutput(step=progress,
                                     count=len(traders)))

    @property
    def traders(self) -> tuple[Trader, ...]:
        return self._runners

    @property
    def result(self) -> Result:
        try:
            return Result(*self._digests)
        except AttributeError:
            return Result(*[r.digest for r in self._runners])

    @override
    def run(self, *, mode: Mode = 'process') -> Self:
        # start monitor
        t = Thread(target=monitor.run,
                   name='Monitor')
        t.start()

        # run all the traders
        match(mode):
            case 'serial':
                self._run_sync()
            case 'thread':
                self._run_async()
            case 'process':
                self._run_multiprocess()
            case _:
                self._run_async()

        # stop monitor
        monitor.put(Exit())
        t.join()

        # return bt
        return self
