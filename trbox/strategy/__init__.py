from threading import Event
from trbox.event import Price
from trbox.event.handler import EventHandler


class Strategy(EventHandler):
    def handle(self, e: Event):
        if isinstance(e, Price):
            print(f'St: price={e.price}')
