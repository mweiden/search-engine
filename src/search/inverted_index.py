from dataclasses import dataclass, field
from collections import defaultdict

import hnswlib
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
        self._words_per_doc: dict[str, int] = defaultdict(int)
        self._doc_id_to_url: dict[str, str] = dict()
        self._doc_id_to_title: dict[str, str] = dict()
        self._model = model if model is not None else SentenceTransformer(model_name)
        embedding_dim = self._model.get_sentence_embedding_dimension()
        self._hnsw = hnswlib.Index(space="cosine", dim=embedding_dim)
        self._hnsw.init_index(max_elements=100_000, ef_construction=200, M=16)
        self._id_to_label: dict[str, int] = {}
        self._label_to_id: dict[int, str] = {}
        self._next_label = 0

    @property
    def total_docs(self):
        return len(self._doc_id_to_url)

    def insert(self, doc: Node) -> None:
        _, total = self._word_count(doc.text)
        self._words_per_doc[doc.id] = total
        self._doc_id_to_url[doc.id] = doc.url
        self._doc_id_to_title[doc.id] = doc.title
        if doc.text is not None:
            embedding = self._model.encode(doc.text).astype(np.float32)
            if self._next_label >= self._hnsw.get_max_elements():
                self._hnsw.resize_index(self._next_label * 2)
            self._hnsw.add_items(embedding, self._next_label)
            self._id_to_label[doc.id] = self._next_label
            self._label_to_id[self._next_label] = doc.id
            self._next_label += 1

    def _word_count(self, text: str) -> dict[str, int]:
        counts = defaultdict(int)
        tokens = tokenize(text)
        total = 0
        for word in tokens:
            counts[word] += 1
            total += 1
        return counts, total

    def num_words_in_doc(self, doc_id: str) -> int:
        return self._words_per_doc[doc_id]

    def top_k(self, query: str, k: int = 10) -> list[SearchResult]:
        if self._next_label == 0:
            return []
        k = min(k, self._next_label)
        query_embedding = self._model.encode(query).astype(np.float32)
        self._hnsw.set_ef(max(k, 10))
        labels, distances = self._hnsw.knn_query(query_embedding, k)
        results = []
        for label, distance in zip(labels[0], distances[0]):
            doc_id = self._label_to_id[label]
            score = 1.0 - float(distance)
            results.append(
                SearchResult(
                    id=doc_id,
                    url=self._doc_id_to_url[doc_id],
                    title=self._doc_id_to_title[doc_id],
                    score=score,
                )
            )
        return results
