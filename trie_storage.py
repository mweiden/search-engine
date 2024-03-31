import os
import pickle
import glob
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from subgraph_cache_trie import SubgraphCacheTrie


@dataclass
class TrieBlob:
    file_path: str
    trie: SubgraphCacheTrie


class TrieStorage:

    def __init__(self, dir: str):
        if not os.path.isdir(dir):
            raise FileNotFoundError(f"Directory does not exist: {dir}")
        self.dir = dir

    def save(self, trie: SubgraphCacheTrie) -> str:
        now = datetime.now()
        formatted_date = now.strftime("%Y%m%d%H%M%S")
        pkl_file_name = f"{self.dir}/trie_{formatted_date}.pkl"
        with open(pkl_file_name, "wb") as file:
            pickle.dump(trie, file)
        return pkl_file_name

    def get_latest_trie(self) -> Optional[TrieBlob]:
        matching_files = glob.glob(f"{self.dir}/trie_*.pkl")
        if not matching_files:
            return None
        latest_file_path = sorted(matching_files)[-1]
        with open(latest_file_path, "rb") as file:
            trie = pickle.load(file)
        return TrieBlob(latest_file_path, trie)
