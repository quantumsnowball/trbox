import time
from trbox.event import Event
from trbox.event.market import Price
from threading import Thread
from trbox.event.system import Start
from trbox.market import Market


class DummyPrice(Market):
    def __init__(self,
                 n: int = 30,
                 delay: int = 1) -> None:
        super().__init__()
        self._n = n
        self._delay = delay

    def simulate_price_feed(self) -> None:
        def worker() -> None:
            # gen random price to simulate live market
            for i in range(self._n):
                self.runner.strategy.put(Price(i))
                time.sleep(self._delay)
            # simulate the end of data
            self.runner.stop()
        # deamon thread will not block program from exiting
        t = Thread(target=worker, daemon=True)
        t.start()

    def handle(self, e: Event) -> None:
        if isinstance(e, Start):
            # generate some dummy price data
            # simulating live feed data from websocket
            self.simulate_price_feed()
