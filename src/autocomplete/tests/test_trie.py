from autocomplete.trie import Trie


def test_insert():
    t = Trie()
    t.insert("all", 1)
    t.insert("any", 2)
    t.insert("an", 3)

    assert t.root.child_keys() == {"a"}
    assert t.root["a"].child_keys() == {"l", "n"}
    assert t.root["a"]["l"].child_keys() == {"l"}
    assert t.root["a"]["n"].child_keys() == {"y"}

    assert t.root["a"].value is None
    assert t.root["a"]["l"]["l"].value == 1
    assert t.root["a"]["n"]["y"].value == 2
    assert t.root["a"]["n"].value == 3

    assert t.root["a"].key == "a"
    assert t.root["a"]["n"].key == "an"
    assert t.root["a"]["l"]["l"].key == "all"
    assert t.root["a"]["n"]["y"].key == "any"

    assert t.root["a"].is_terminal is False
    assert t.root["a"]["n"].is_terminal is True
    assert t.root["a"]["l"]["l"].is_terminal is True
    assert t.root["a"]["n"]["y"].is_terminal is True

    assert t.root.parent is None
    assert t.root["a"].parent == t.root
    assert t.root["a"]["n"].parent == t.root["a"]
    assert t.root["a"]["l"].parent == t.root["a"]
    assert t.root["a"]["l"]["l"].parent == t.root["a"]["l"]
    assert t.root["a"]["n"]["y"].parent == t.root["a"]["n"]


def test_find():
    t = Trie()
    t.insert("all", 1)
    t.insert("any", 2)
    assert t.find("a") == t.root["a"]
    assert t.find("al") == t.root["a"]["l"]
    assert t.find("an") == t.root["a"]["n"]
    assert t.find("all").value == 1
    assert t.find("any").value == 2
    assert t.find("some") is None


def test_delete():
    t = Trie()
    t.insert("all", 1)
    t.insert("any", 2)
    t.insert("an", 3)
    assert t.find("all").value == 1
    assert t.find("any").value == 2
    assert t.find("an").value == 3
    assert t.find("an").is_terminal is True
    # delete a leaf
    t.delete("all")
    assert t.root["a"].child_keys() == {"n"}
    assert t.find("all") is None
    assert t.find("any").value == 2
    # delete an inner node
    t.delete("an")
    assert t.root["a"]["n"].child_keys() == {"y"}
    assert t.find("an") is not None
    assert t.find("an").is_terminal is False
    # delete a non-existant key
    assert t.delete("some") is None
