import time
from trbox.event import Price, PriceFeedRequest
from trbox.event.handler import EventHandler


class Market(EventHandler):
    def handle(self, e):
        if isinstance(e, PriceFeedRequest):
            # generate some dummy price data
            for i in range(30):
                self.runner.strategy.put(Price(i))
                time.sleep(1)
