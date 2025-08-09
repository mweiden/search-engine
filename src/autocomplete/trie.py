from collections import deque

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Set


@dataclass
class Node:
    key: str
    value: Any
    children: Dict[str, "Node"] = field(default_factory=dict)
    is_terminal: bool = field(default=False)
    parent: "Node" = field(default=None)

    def __getitem__(self, key) -> "Node":
        return self.children[key]

    def __setitem__(self, key, value):
        self.children[key] = value

    def get(self, key) -> Optional["Node"]:
        return self[key] if key in self.children else None

    def child_keys(self) -> Set[str]:
        return set(self.children.keys())


class Trie:
    def __init__(self, node_type: Node = Node):
        self.node_type = node_type
        self.root: Node = node_type("", None)

    def insert(self, key, value) -> Node:
        current_node = self.root
        for c in key:
            if current_node.get(c) is None:
                new_node = self.node_type(current_node.key + c, None)
                new_node.parent = current_node
                current_node[c] = new_node
            current_node = current_node[c]
        current_node.value = value
        current_node.is_terminal = True
        return current_node

    def delete(self, key: str):
        def inner(node, key) -> Optional[Node]:
            if key == "":
                if node.is_terminal:
                    node.is_terminal = False
                    node.value = None
                return node if node.children else None
            if key[0] not in node.children:
                return node
            child = inner(node[key[0]], key[1:])
            if child is None:
                del node.children[key[0]]
            else:
                node[key[0]] = child
            return node if node.children or node.is_terminal else None

        inner(self.root, key)

    def find(self, key: str) -> Optional[Node]:
        current_node = self.root
        for c in key:
            if c not in current_node.children:
                return None
            current_node = current_node[c]
        return current_node

    def bfs(self):
        queue = deque([self.root])
        visited = set([])

        while queue:
            current_node = queue.popleft()
            visited.add(current_node.key)
            queue.extend(
                child
                for _, child in current_node.children.items()
                if child.key not in visited
            )
            yield current_node
