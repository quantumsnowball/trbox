from dataclasses import dataclass

from pandas import Timestamp

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
    timestamp: Timestamp
    symbol: Symbol


class PortfolioEvent(Event):
    '''
    equity curve / trade log / metrics
    '''
    pass


class SystemEvent(Event):
    '''
    Flow control of the Runner
    '''
    pass
