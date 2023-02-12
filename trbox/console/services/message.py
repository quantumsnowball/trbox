import json
from abc import ABC, abstractmethod
from typing import Generic, Literal, TypeVar

from typing_extensions import override

from trbox.event.portfolio import OrderResultUpdate

# a list of defined tags that the frontend is willing to handle
Tag = Literal[
    'OrderResult'
]

T = TypeVar('T')

# the only object that is accept by the websocket.send()


class Message(Generic[T], ABC):
    def __init__(self,
                 tag: Tag,
                 data: T) -> None:
        self._tag = tag
        self._data = data

    @property
    @abstractmethod
    def json(self) -> str:
        '''
        Flatten the object into fields of string value
        Avoid nesting to guarantee the correct result when serialized
        '''
        pass

# unpacka and repack the info as simple as possible


class OrderResult(Message[OrderResultUpdate]):
    def __init__(self,
                 data: OrderResultUpdate) -> None:
        super().__init__('OrderResult', data)

    @property
    @override
    def json(self) -> str:
        d = self._data.order_result
        packed = dict(
            tag=self._tag,
            data=dict(
                timestamp=d.timestamp.isoformat(),
                symbol=d.order.symbol,
                action=d.action,
                price=d.price,
                quantity=d.quantity,
            )
        )
        return json.dumps(packed)
