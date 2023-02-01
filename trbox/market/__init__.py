from abc import ABC

from trbox.event.handler import CounterParty


class Market(CounterParty, ABC):
    '''
    Market extens CounterParty interface.

    It is the interface for different types of Market like object.
    It should make sence to both live and generated data source.
    '''
