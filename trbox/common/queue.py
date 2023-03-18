import threading
from collections import deque
from typing import Any, Generic, TypeVar

T = TypeVar('T')


class MTQueue(Generic[T]):
    """
    This is intended to be drop in replacement for queue.Queue
    Also operations must be thread-safe, can be use between multiple threads
    Never use across multiple processes
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._queue = deque[T](*args, **kwargs)
        self._ready = threading.Event()

    def put(self, e: T) -> None:
        self._queue.append(e)
        self._ready.set()

    def get(self) -> T:
        while True:
            try:
                self._ready.wait()
                e = self._queue.popleft()
                return e
            except IndexError:
                self._ready.clear()
