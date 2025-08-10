import numpy as np
import pytest
import requests
from sentence_transformers import SentenceTransformer

from web_crawler.node import Node
from search.inverted_index import InvertedIndex, SearchResult
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
def inverted_index(node0, node1) -> InvertedIndex:
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
    inverted_index = InvertedIndex(model=model)
    inverted_index.insert(node0)
    inverted_index.insert(node1)
    return inverted_index


@pytest.fixture
def search_result0(node0) -> SearchResult:
    return SearchResult(node0.id, node0.url, node0.title)


@pytest.fixture
def search_result1(node1) -> SearchResult:
    return SearchResult(node1.id, node1.url, node1.title)


def test_insert(inverted_index, search_result0, search_result1):
    assert list(tokenize("ipsum")) == ["ipsum"]
    assert list(tokenize("iterators")) == ["iterators"]
    assert inverted_index.search("ipsum") == [search_result0]
    assert inverted_index.search("iterators") == [search_result0, search_result1]


def test_num_words_in_doc(inverted_index, node0, node1):
    node0_tokens = list(tokenize(node0.text))
    node1_tokens = list(tokenize(node1.text))
    assert inverted_index.num_words_in_doc(node0.id) == len(node0_tokens)
    assert inverted_index.num_words_in_doc(node1.id) == len(node1_tokens)


def test_top_k_cosine(inverted_index, node0, node1):
    results = inverted_index.top_k("lorem ipsum")
    assert results[0].id == node0.id

    results = inverted_index.top_k("type hint iterators")
    assert [r.id for r in results[:2]] == [node1.id, node0.id]


def test_paraphrase_minilm_model_simple_example():
    model = SentenceTransformer("sentence-transformers/paraphrase-MiniLM-L3-v2")

    index = InvertedIndex(model=model)

    sky = Node(
        raw_url="https://example.com/sky",
        text="The sky is blue.",
        title="sky",
    )
    car = Node(
        raw_url="https://example.com/car",
        text="Driving my car is fun.",
        title="car",
    )
    index.insert(sky)
    index.insert(car)

    results = index.top_k("blue sky")
    assert results[0].id == sky.id

    results = index.top_k("my car")
    assert results[0].id == car.id
