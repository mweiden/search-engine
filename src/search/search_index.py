from dataclasses import dataclass, field
from collections import defaultdict, OrderedDict

import hnswlib
import numpy as np
from sentence_transformers import CrossEncoder, SentenceTransformer

from web_crawler.node import Node
from search.tokenizer import tokenize


@dataclass
class SearchResult:
    id: str
    url: str
    title: str | None = field(default=None)
    score: float | None = field(default=None)


class SearchIndex:

    def __init__(
        self,
        model: SentenceTransformer | None = None,
        model_name: str = "sentence-transformers/paraphrase-MiniLM-L3-v2",
        cross_encoder: CrossEncoder | None = None,
        cross_encoder_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        cache_size: int = 1_000,
    ):
        self._inverted_index: dict[str, list[tuple[str, int]]] = defaultdict(list)
        self._words_per_doc: dict[str, int] = defaultdict(int)
        self._doc_id_to_url: dict[str, str] = dict()
        self._doc_id_to_title: dict[str, str] = dict()
        self._doc_id_to_text: dict[str, str] = dict()
        self._model = model if model is not None else SentenceTransformer(model_name)
        embedding_dim = self._model.get_sentence_embedding_dimension()
        self._hnsw = hnswlib.Index(space="cosine", dim=embedding_dim)
        self._hnsw.init_index(max_elements=100_000, ef_construction=200, M=16)
        self._id_to_label: dict[str, int] = {}
        self._label_to_id: dict[int, str] = {}
        self._next_label = 0
        if cross_encoder is not None:
            self._cross_encoder = cross_encoder
        elif cross_encoder_name is not None:
            self._cross_encoder = CrossEncoder(cross_encoder_name)
        else:
            self._cross_encoder = None
        self._score_cache: OrderedDict[tuple[str, str], float] = OrderedDict()
        self._cache_size = cache_size

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
            self._doc_id_to_text[doc.id] = doc.text
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

    def set_cross_encoder(self, cross_encoder: CrossEncoder) -> None:
        self._cross_encoder = cross_encoder

    def top_k(
        self, query: str, k: int = 10, candidates: int | None = None
    ) -> list[SearchResult]:
        if self._next_label == 0:
            return []
        candidates = self._next_label if candidates is None else candidates
        candidates = min(max(k, candidates), self._next_label)
        query_embedding = self._model.encode(query).astype(np.float32)
        self._hnsw.set_ef(max(candidates, 10))
        labels, distances = self._hnsw.knn_query(query_embedding, candidates)
        results = []
        for label in labels[0]:
            doc_id = self._label_to_id[label]
            results.append(
                SearchResult(
                    id=doc_id,
                    url=self._doc_id_to_url[doc_id],
                    title=self._doc_id_to_title[doc_id],
                    score=None,
                )
            )
        if self._cross_encoder is None:
            for result, distance in zip(results, distances[0]):
                result.score = 1.0 - float(distance)
            return results[:k]
        missing: list[SearchResult] = []
        pairs: list[tuple[str, str]] = []
        for result in results:
            text = self._doc_id_to_text.get(result.id, "")
            key = (query, result.id)
            if key in self._score_cache:
                self._score_cache.move_to_end(key)
                result.score = self._score_cache[key]
            else:
                missing.append(result)
                pairs.append((query, text))
        if pairs:
            scores = self._cross_encoder.predict(pairs)
            for result, score in zip(missing, scores):
                result.score = float(score)
                key = (query, result.id)
                self._score_cache[key] = result.score
                self._score_cache.move_to_end(key)
                if len(self._score_cache) > self._cache_size:
                    self._score_cache.popitem(last=False)
        results.sort(
            key=lambda r: r.score if r.score is not None else float("-inf"),
            reverse=True,
        )
        return results[:k]
