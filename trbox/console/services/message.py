import json
from abc import ABC, abstractmethod
from typing import Generic, Literal, TypeVar

from typing_extensions import override

from trbox.event.portfolio import (EquityCurveHistoryUpdate, EquityCurveUpdate,
                                   OrderResultUpdate)

# a list of defined tags that the frontend is willing to handle
Tag = Literal[
    'EquityValue',
    'EquityCurveHistory',
    'OrderResult',
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


class EquityCurve(Message[EquityCurveUpdate]):
    def __init__(self,
                 data: EquityCurveUpdate) -> None:
        super().__init__('EquityValue', data)

    @property
    @override
    def json(self) -> str:
        d = self._data
        packed = dict(
            tag=self._tag,
            data=dict(
                timestamp=d.timestamp.isoformat(),
                equity=d.equity
            )
        )
        return json.dumps(packed)


class EquityCurveHistory(Message[EquityCurveHistoryUpdate]):
    def __init__(self,
                 data: EquityCurveHistoryUpdate) -> None:
        super().__init__('EquityCurveHistory', data)

    @property
    @override
    def json(self) -> str:
        d = self._data
        packed = dict(
            tag=self._tag,
            data=[dict(timestamp=t.isoformat(), equity=v)
                  for t, v in d.series.items()]
        )
        return json.dumps(packed)
