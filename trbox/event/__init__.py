from dataclasses import dataclass
from trbox.common.types import Symbol


class Event:
    pass


class BrokerEvent(Event):
    '''
    Trade orders / account info
    '''
    pass


@dataclass
class MarketEvent(Event):
    '''
    All price data related events
    '''
    symbol: Symbol


class SystemEvent(Event):
    '''
    Flow control of the Runner
    '''
    pass
