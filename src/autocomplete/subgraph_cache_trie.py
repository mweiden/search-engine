from dataclasses import dataclass, field
from typing import Dict, Any, List

from autocomplete.trie import Node, Trie


@dataclass
class SubgraphCacheNode(Node):
    cache: Dict[str, Any] = field(default_factory=dict)
    is_dirty: bool = field(default=False)
    _cache_sorted_keys: List[str] = field(default_factory=list)

    @property
    def cache_sorted_keys(self):
        """cache_sorted_keys

        For faster access, we only want to sort the keys in the cache once per
        unique combination of keys. We do this by maintaining whether there have
        been insertions or deletions in the `is_dirty` state. We can skip
        sorting the list when no writes have been performed.
        """
        if self.is_dirty:
            self._cache_sorted_keys = [
                ele[0]
                for ele in sorted(
                    self.cache.items(),
                    key=lambda kv: kv[1],
                    reverse=True,
                )
            ]
            self.is_dirty = False
        return self._cache_sorted_keys


class SubgraphCacheTrie(Trie):

    def __init__(self):
        super().__init__(node_type=SubgraphCacheNode)

    def insert(self, key, value):
        node = super().insert(key, value)
        node.cache[node.key] = node.value
        node.is_dirty = True
        for ancestor in self._ancestors(node):
            ancestor.cache[node.key] = node.value
            ancestor.is_dirty = True

    def delete(self, key):
        node = self.find(key)
        if node is None:
            return
        super().delete(key)
        del node.cache[node.key]
        node.is_dirty = True
        for ancestor in self._ancestors(node):
            del ancestor.cache[node.key]
            ancestor.is_dirty = True

    @staticmethod
    def _ancestors(node: SubgraphCacheNode):
        ancestor = node.parent
        while ancestor is not None:
            yield ancestor
            ancestor = ancestor.parent
