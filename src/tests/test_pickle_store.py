import tempfile

from pickle_store import PickleStore
from autocomplete.subgraph_cache_trie import SubgraphCacheTrie


def test_save():
    with tempfile.TemporaryDirectory() as temp_dir:
        trie_storage = PickleStore(temp_dir)
        assert trie_storage.get_latest(SubgraphCacheTrie) is None
        trie = SubgraphCacheTrie()
        trie_storage.save(trie)


def test_get_latest():
    with tempfile.TemporaryDirectory() as temp_dir:
        trie_storage = PickleStore(temp_dir)
        first_trie = SubgraphCacheTrie()
        second_trie = SubgraphCacheTrie()

        first_trie.insert("first!", 1)
        second_trie.insert("second!", 2)

        trie_storage.save(first_trie)
        assert (
            trie_storage.get_latest(SubgraphCacheTrie).artifact.find("first!").value
            == 1
        )
        trie_storage.save(second_trie)
        assert (
            trie_storage.get_latest(SubgraphCacheTrie).artifact.find("second!").value
            == 2
        )
