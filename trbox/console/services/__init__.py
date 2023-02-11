from abc import ABC, abstractmethod
from asyncio import AbstractEventLoop, new_event_loop, run_coroutine_threadsafe
from threading import Thread
from typing import Any

from typing_extensions import override


class Service(Thread, ABC):
    def __init__(self,
                 *args: Any,
                 port: int,
                 **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._port = port
        self._loop: AbstractEventLoop | None = None

    #
    # props
    #
    @property
    def port(self) -> int:
        return self._port

    #
    # main service
    #
    @abstractmethod
    async def main(self):
        pass

    @override
    def run(self):
        self._loop = new_event_loop()
        self._loop.run_until_complete(self.main())

    #
    # assign more tasks
    #
    def create_task(self, coro):
        assert self._loop is not None
        run_coroutine_threadsafe(coro, self._loop)
