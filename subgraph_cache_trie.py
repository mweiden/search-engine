from dataclasses import dataclass
from typing import Dict, Any

from trie import Node, Trie


@dataclass
class SubgraphCacheNode(Node):
    cache: Dict[str, Any]


class SubgraphCacheTrie(Trie):

    def __init__(self):
        super().__init__(node_type=SubgraphCacheNode)

    def insert(self, key, value):
        node = super().insert(key, value)
        for ancestor in SubgraphCacheTrie._ancestors(node):
            ancestor.cache[node.key] = node.value

    def delete(self, key):
        node = self.find(key)
        if node is None:
            return
        super().delete(key)
        for ancestor in SubgraphCacheTrie._ancestors(node):
            del ancestor.cache[node.key]

    @staticmethod
    def _ancestors(node: Node):
        ancestor = node.parent
        while ancestor is not None:
            yield ancestor
            ancestor = ancestor.parent
