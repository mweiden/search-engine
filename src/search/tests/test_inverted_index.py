import pytest

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
    inverted_index = InvertedIndex()
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


def test_top_k_tf_idf(inverted_index, node0, node1):
    expected = [
        SearchResult(node0.id, node0.url, node0.title, 0.1267494718585184),
    ]
    assert inverted_index.top_k_tf_idf("lorem ipsum") == expected
    expected = [
        SearchResult(node1.id, node1.url, node1.title, 0.2454477634937209),
        SearchResult(node0.id, node0.url, node0.title, 0.0541067749263286),
    ]
    assert inverted_index.top_k_tf_idf("type hint iterators") == expected
