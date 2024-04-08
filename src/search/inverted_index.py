from dataclasses import dataclass, field
from math import log10
from collections import defaultdict

from web_crawler.node import Node
from search.tokenizer import tokenize


@dataclass
class SearchResult:
    id: str
    url: str
    title: str | None = field(default=None)
    tf_idf: float | None = field(default=None)


class InvertedIndex:

    def __init__(self):
        self._inverted_index: dict[str, list[tuple[str, int]]] = defaultdict(list)
        self._words_per_doc: dict[str, int] = defaultdict(int)
        self._doc_id_to_url: dict[str, str] = dict()
        self._doc_id_to_title: dict[str, str] = dict()

    @property
    def total_docs(self):
        return len(self._inverted_index)

    def insert(self, doc: Node) -> None:
        counts, total = self._word_count(doc.text)
        for word, count in counts.items():
            self._inverted_index[word].append((doc.id, count))
        self._words_per_doc[doc.id] = total
        self._doc_id_to_url[doc.id] = doc.url
        self._doc_id_to_title[doc.id] = doc.title

    def _word_count(self, text: str) -> dict[str, int]:
        counts = defaultdict(int)
        tokens = tokenize(text)
        total = 0
        for word in tokens:
            counts[word] += 1
            total += 1
        return counts, total

    def _search(self, word: str) -> list[tuple[str, int]]:
        result = self._inverted_index.get(word)
        return [] if result is None else result

    def search(self, word: str) -> list[SearchResult]:
        return [
            SearchResult(
                id=kv[0],
                url=self._doc_id_to_url[kv[0]],
                title=self._doc_id_to_title[kv[0]],
                tf_idf=None,
            )
            for kv in self._search(word)
        ]

    def num_words_in_doc(self, doc_id: str) -> int:
        return self._words_per_doc[doc_id]

    def top_k_tf_idf(self, query: str, k: int = 10) -> list[SearchResult]:
        query_tokens = tokenize(query)
        tf_idf = defaultdict(float)
        for word in query_tokens:
            results = self._search(word)
            for doc_id, count in results:
                doc_total = self.num_words_in_doc(doc_id)

                tf = count / float(doc_total)
                idf = log10(self.total_docs / (1.0 + len(results)))
                tf_idf[doc_id] += tf * idf

        return [
            SearchResult(
                id=kv[0],
                url=self._doc_id_to_url[kv[0]],
                title=self._doc_id_to_title[kv[0]],
                tf_idf=kv[1],
            )
            for kv in sorted(tf_idf.items(), reverse=True, key=lambda kv: kv[1])[:k]
        ]
