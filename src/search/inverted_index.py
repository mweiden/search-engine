from dataclasses import dataclass, field
from collections import defaultdict

import numpy as np
from sentence_transformers import SentenceTransformer

from web_crawler.node import Node
from search.tokenizer import tokenize


@dataclass
class SearchResult:
    id: str
    url: str
    title: str | None = field(default=None)
    score: float | None = field(default=None)


class InvertedIndex:

    def __init__(
        self,
        model: SentenceTransformer | None = None,
        model_name: str = "sentence-transformers/paraphrase-MiniLM-L3-v2",
    ):
        self._inverted_index: dict[str, list[tuple[str, int]]] = defaultdict(list)
        self._words_per_doc: dict[str, int] = defaultdict(int)
        self._doc_id_to_url: dict[str, str] = dict()
        self._doc_id_to_title: dict[str, str] = dict()
        self._doc_embeddings: dict[str, np.ndarray] = dict()
        self._model = model if model is not None else SentenceTransformer(model_name)

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
        if doc.text is not None:
            self._doc_embeddings[doc.id] = self._model.encode(doc.text)

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
                score=None,
            )
            for kv in self._search(word)
        ]

    def num_words_in_doc(self, doc_id: str) -> int:
        return self._words_per_doc[doc_id]

    def top_k(self, query: str, k: int = 10) -> list[SearchResult]:
        query_embedding = self._model.encode(query)
        scores: dict[str, float] = {}
        for doc_id, embedding in self._doc_embeddings.items():
            similarity = float(
                np.dot(query_embedding, embedding)
                / (np.linalg.norm(query_embedding) * np.linalg.norm(embedding))
            )
            scores[doc_id] = similarity

        return [
            SearchResult(
                id=doc_id,
                url=self._doc_id_to_url[doc_id],
                title=self._doc_id_to_title[doc_id],
                score=score,
            )
            for doc_id, score in sorted(
                scores.items(), key=lambda kv: kv[1], reverse=True
            )[:k]
        ]
