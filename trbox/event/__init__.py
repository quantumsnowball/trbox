from dataclasses import dataclass

from pandas import Timestamp


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
    timestamp: Timestamp


class SystemEvent(Event):
    '''
    Flow control of the Runner
    '''
    pass
