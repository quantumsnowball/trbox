class Event:
    pass


class BrokerEvent(Event):
    '''
    Trade orders / account info
    '''
    pass


class MarketEvent(Event):
    '''
    Price data request / response
    '''
    pass


class SystemEvent(Event):
    '''
    Flow control of the Runner
    '''
    pass
