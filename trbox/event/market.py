from trbox.event import Event


class MarketEvent(Event):
    pass


class PriceFeedRequest(MarketEvent):
    def __init__(self,
                 symbol: str):
        self._symbol = symbol


class Price(MarketEvent):
    def __init__(self, price: float):
        self._price = price

    @property
    def price(self):
        return self._price
