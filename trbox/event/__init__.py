from dataclasses import dataclass


class Event:
    pass


class BrokerEvent(Event):
    """
    Trade orders / account info
    """

    pass


@dataclass
class MarketEvent(Event):
    """
    All price data related events
    """


class SystemEvent(Event):
    """
    Flow control of the Runner
    """

    pass
