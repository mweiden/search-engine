from autocomplete.trie import Trie
from autocomplete.mermaid import Mermaid


def test_mermaid_graph():
    mmd = Mermaid()
    t = Trie()
    t.insert("all", 1)
    t.insert("any", 2)
    t.insert("an", 3)
    assert (
        mmd.render_trie(t)
        == """graph TD
\tn0[ ]
\tn1[a]
\tn2[l]
\tn3[n]
\tn4[l]
\tn5[y]
\tn0 --> n1
\tn1 --> n2
\tn1 --> n3
\tn2 --> n4
\tn3 --> n5
"""
    )
