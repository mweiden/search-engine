import numpy as np
import pytest

from web_crawler.node import Node
from search.search_index import SearchIndex, SearchResult
from search.tokenizer import tokenize


@pytest.fixture
def node0() -> Node:
    return Node(
        raw_url="https://some.page.on.the.internet",
        text=(
            "In publishing and graphic design, Lorem ipsum is a placeholder text "
            "commonly used to demonstrate the visual form of a document or a typeface "
            "without relying on meaningful content iterators."
        ),
        title="lorem ipsum",
    )


@pytest.fixture
def node1() -> Node:
    return Node(
        raw_url="https://some.other.page.on.the.internet",
        text=(
            "For clarity and correctness in type hints, you should use Iterable and/or "
            "Iterator from the typing module to annotate functions that return iterators."
        ),
        title="iterable/iterator",
    )


@pytest.fixture
def search_index(node0, node1) -> SearchIndex:
    class DummyModel:
        KEYWORDS0 = {"lorem", "ipsum"}
        KEYWORDS1 = {"type", "hint", "iterators", "iterator"}

        def encode(self, text: str) -> np.ndarray:
            tokens = text.lower().split()
            vec = np.array(
                [
                    sum(t in self.KEYWORDS0 for t in tokens),
                    sum(t in self.KEYWORDS1 for t in tokens),
                ],
                dtype=np.float32,
            )
            if not vec.any():
                vec = np.array([len(tokens), 0.0], dtype=np.float32)
            return vec

        def get_sentence_embedding_dimension(self) -> int:
            return 2

    model = DummyModel()
    index = SearchIndex(model=model, cross_encoder=None, cross_encoder_name=None)
    index.insert(node0)
    index.insert(node1)
    return index


@pytest.fixture
def search_result0(node0) -> SearchResult:
    return SearchResult(node0.id, node0.url, node0.title)


@pytest.fixture
def search_result1(node1) -> SearchResult:
    return SearchResult(node1.id, node1.url, node1.title)


def test_insert(search_index, search_result0, search_result1):
    assert list(tokenize("ipsum")) == ["ipsum"]
    assert list(tokenize("iterators")) == ["iterators"]
    assert search_index.search("ipsum") == [search_result0]
    assert search_index.search("iterators") == [search_result0, search_result1]


def test_num_words_in_doc(search_index, node0, node1):
    node0_tokens = list(tokenize(node0.text))
    node1_tokens = list(tokenize(node1.text))
    assert search_index.num_words_in_doc(node0.id) == len(node0_tokens)
    assert search_index.num_words_in_doc(node1.id) == len(node1_tokens)


def test_top_k_cosine(search_index, node0, node1):
    results = search_index.top_k("lorem ipsum")
    assert results[0].id == node0.id

    results = search_index.top_k("type hint iterators")
    assert [r.id for r in results[:2]] == [node1.id, node0.id]


def test_cross_encoder_rerank_and_cache(node0, node1):
    class DummyModel:
        KEYWORDS0 = {"lorem", "ipsum"}
        KEYWORDS1 = {"type", "hint", "iterators", "iterator"}

        def encode(self, text: str) -> np.ndarray:
            tokens = text.lower().split()
            vec = np.array(
                [
                    sum(t in self.KEYWORDS0 for t in tokens),
                    sum(t in self.KEYWORDS1 for t in tokens),
                ],
                dtype=np.float32,
            )
            if not vec.any():
                vec = np.array([len(tokens), 0.0], dtype=np.float32)
            return vec

        def get_sentence_embedding_dimension(self) -> int:
            return 2

    class DummyCrossEncoder:
        def __init__(self):
            self.call_count = 0

        def predict(self, pairs):
            self.call_count += len(pairs)
            scores = []
            for _, text in pairs:
                scores.append(2.0 if "lorem" in text.lower() else 1.0)
            return scores

    model = DummyModel()
    cross_encoder = DummyCrossEncoder()
    index = SearchIndex(model=model, cross_encoder=cross_encoder)
    index.insert(node0)
    index.insert(node1)

    results = index.top_k("type hint iterators", k=2, candidates=2)
    assert [r.id for r in results] == [node0.id, node1.id]
    assert cross_encoder.call_count == 2

    # second call uses cache, so cross_encoder isn't invoked again
    index.top_k("type hint iterators", k=2, candidates=2)
    assert cross_encoder.call_count == 2


def test_paraphrase_minilm_model_simple_example():
    pytest.skip(
        "requires downloading a large SentenceTransformer model",
        allow_module_level=False,
    )
