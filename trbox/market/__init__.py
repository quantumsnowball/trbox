import time
from trbox.event import Price, PriceFeedRequest
from trbox.event.handler import EventHandler


class Market(EventHandler):
    def handle(self, e):
        if isinstance(e, PriceFeedRequest):
            for i in range(30):
                self._runner._strategy.put(Price(i))
                time.sleep(1)
