from dataclasses import dataclass, field
from typing import Dict, Any

from trie import Node, Trie


@dataclass
class SubgraphCacheNode(Node):
    cache: Dict[str, Any] = field(default_factory=dict)


class SubgraphCacheTrie(Trie):

    def __init__(self):
        super().__init__(node_type=SubgraphCacheNode)

    def insert(self, key, value):
        node = super().insert(key, value)
        node.cache[node.key] = node.value
        for ancestor in self._ancestors(node):
            ancestor.cache[node.key] = node.value

    def delete(self, key):
        node = self.find(key)
        if node is None:
            return
        super().delete(key)
        for ancestor in self._ancestors(node):
            del ancestor.cache[node.key]

    @staticmethod
    def _ancestors(node: SubgraphCacheNode):
        ancestor = node.parent
        while ancestor is not None:
            yield ancestor
            ancestor = ancestor.parent
