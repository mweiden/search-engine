from subgraph_cache_trie import SubgraphCacheTrie


def test_insert():
    t = SubgraphCacheTrie()
    t.insert("all", 1)
    t.insert("any", 2)
    t.insert("an", 3)
    assert t.root.cache == {"all": 1, "any": 2, "an": 3}
    assert t.root["a"].cache == {"all": 1, "any": 2, "an": 3}
    assert t.root["a"]["l"].cache == {"all": 1}
    assert t.root["a"]["n"].cache == {"any": 2, "an": 3}

def test_delete():
    t = SubgraphCacheTrie()
    t.insert("all", 1)
    t.insert("any", 2)
    t.insert("an", 3)
    t.delete("all")
    assert t.find("all") is None
    assert t.root.cache == {"any": 2, "an": 3}
    assert t.root["a"].cache == {"any": 2, "an": 3}
    assert t.root["a"]["n"].cache == {"any": 2, "an": 3}