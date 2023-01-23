import time
from trbox.event import Event
from trbox.event.market import Price, PriceFeedRequest
from threading import Thread
from trbox.market import Market


class DummyPrice(Market):
    def simulate_price_feed(self, n=30):
        def worker():
            for i in range(n):
                self.runner.strategy.put(Price(i))
                time.sleep(1)
        # deamon thread will not block program from exiting
        t = Thread(target=worker, daemon=True)
        t.start()

    def handle(self, e: Event):
        if isinstance(e, PriceFeedRequest):
            # generate some dummy price data
            # simulating live feed data from websocket
            self.simulate_price_feed()
