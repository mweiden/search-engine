import os
import pickle
import glob
from dataclasses import dataclass
from typing import Optional, Type
from datetime import datetime

from autocomplete.subgraph_cache_trie import SubgraphCacheTrie
from search.inverted_index import InvertedIndex


@dataclass
class Artifact:
    file_path: str
    artifact: SubgraphCacheTrie | InvertedIndex


class PickleStore:

    def __init__(self, dir: str):
        if not os.path.isdir(dir):
            raise FileNotFoundError(f"Directory does not exist: {dir}")
        self.dir = dir

    def save(self, obj: SubgraphCacheTrie | InvertedIndex) -> str:
        now = datetime.now()
        formatted_date = now.strftime("%Y%m%d%H%M%S")
        file_prefix = self._file_prefix(type(obj))
        pkl_file_name = f"{self.dir}/{file_prefix}_{formatted_date}.pkl"
        with open(pkl_file_name, "wb") as file:
            pickle.dump(obj, file)
        return pkl_file_name

    def get_latest(self, typ: SubgraphCacheTrie | InvertedIndex) -> Optional[Artifact]:
        file_prefix = self._file_prefix(typ)
        matching_files = glob.glob(f"{self.dir}/{file_prefix}_*.pkl")
        if not matching_files:
            return None
        latest_file_path = sorted(matching_files)[-1]
        with open(latest_file_path, "rb") as file:
            trie = pickle.load(file)
        return Artifact(latest_file_path, trie)

    def _file_prefix(self, typ: Type) -> str:
        if typ == SubgraphCacheTrie:
            return "trie"
        elif typ == InvertedIndex:
            return "inverted_index"
