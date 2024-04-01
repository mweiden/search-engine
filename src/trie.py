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
        def inner(node, key) -> Node:
            if key == "":
                if node.is_terminal:
                    node.is_terminal = False
                    node.value = None
                return node if len(node.children) > 0 else None
            if key[0] not in node.children:
                return None
            node[key[0]] = inner(node[key[0]], key[1:])
            return node

        inner(self.root, key)

    def find(self, key: str) -> Optional[Node]:
        current_node = self.root
        for c in key:
            if c not in current_node.children:
                return None
            current_node = current_node[c]
        return current_node

    def _bfs(self):
        queue = deque([self.root])
        visited = set([])

        while queue:
            current_node = queue.popleft()
            visited.add(current_node.key)
            queue.extend(
                child for _, child in current_node.children.items()
                if child.key not in visited
            )
            yield current_node
    
    def mermaid_graph(self) -> str:
        node_ids = {"": "n0", "counter": 0}
        def _node_id(node: Node) -> str:
            if node.key not in node_ids:
                node_ids["counter"] += 1
                node_ids[node.key] = f"n{node_ids["counter"]}"
            return node_ids[node.key]
        def _node_name(node: Node) -> str:
            if node.key == "":
                return " "
            return node.key[-1]
        mermaid_text = "graph TD\n"
        # declare nodes
        for node in self._bfs():
            mermaid_text += f"\t{_node_id(node)}[{_node_name(node)}]\n"
        for node in self._bfs():
            if node.parent is None:
                continue
            mermaid_text += f"\t{_node_id(node.parent)} --> {_node_id(node)}\n"
        return mermaid_text