import json
from dataclasses import dataclass
from typing import Literal, Union

NodeDict = dict[str, Union[str, list['NodeDict']]]


@dataclass
class Node:
    name: str
    type: Literal['folder', 'file']
    parent: Union['Node', None]
    children: list['Node']

    def add(self, node: 'Node') -> None:
        self.children.append(node)

    @property
    def path(self) -> str:
        if self.parent is None:
            return ''
        return f'{self.parent.path}/{self.name}'

    @property
    def dict(self) -> NodeDict:
        return {
            'name': self.name,
            'type': self.type,
            'path': self.path,
            'children': [c.dict
                         for c in self.children]
        }

    @property
    def json(self) -> str:
        return json.dumps(self.dict, indent=4)
