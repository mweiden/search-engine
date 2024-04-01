from typing import Dict
from trie import Node, Trie


class Mermaid:

    def __init__(self):
        self.node_ids: Dict[str, str] = dict()
        self.node_counter: int = -1

    def _id(self, node: Node) -> str:
        if node.key not in self.node_ids:
            self.node_counter += 1
            self.node_ids[node.key] = f"n{self.node_counter}"
        return self.node_ids[node.key]

    def _name(self, node: Node) -> str:
        if node.key == "":
            return " "
        return node.key[-1]

    def render_trie(self, trie: Trie) -> str:
        mermaid_text = "graph TD\n"
        # declare nodes
        for node in trie.bfs():
            mermaid_text += f"\t{self._id(node)}[{self._name(node)}]\n"
        for node in trie.bfs():
            if node.parent is None:
                continue
            mermaid_text += f"\t{self._id(node.parent)} --> {self._id(node)}\n"
        return mermaid_text
