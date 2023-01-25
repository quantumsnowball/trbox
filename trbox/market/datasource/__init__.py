from typing import Self
from trbox.runner import Runner


class DataSource:
    '''
    DataSource is not a EventHandler, and does not have any event queue.
    It handles data for Market, and can access runner for putting events
    to other handlers.
    '''

    def attach(self, runner: Runner) -> Self:
        self._runner = runner
        return self

    @property
    def runner(self) -> Runner:
        return self._runner
