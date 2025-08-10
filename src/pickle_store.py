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

        # Torch pickles may contain tensors saved on non-CPU devices
        # (e.g. Apple's "mps"). When loading on a machine without that
        # device, ``pickle.load`` will raise ``RuntimeError``. To make
        # deserialization robust across environments we temporarily patch
        # PyTorch's MPS deserializer to fall back to CPU storage if MPS is
        # unavailable.
        try:
            import torch.serialization as ts  # type: ignore

            original_mps_deserialize = getattr(ts, "_mps_deserialize", None)
            registry_backup = None

            if original_mps_deserialize is not None:

                def _cpu_deserialize(storage, location):  # type: ignore
                    return storage.cpu()

                ts._mps_deserialize = _cpu_deserialize  # type: ignore

                # Patch the internal registry used by ``default_restore_location``
                if hasattr(ts, "_package_registry"):
                    for idx, (prio, tag_fn, deser_fn) in enumerate(
                        ts._package_registry
                    ):
                        if deser_fn is original_mps_deserialize:
                            registry_backup = (idx, (prio, tag_fn, deser_fn))
                            ts._package_registry[idx] = (prio, tag_fn, _cpu_deserialize)
                            break

            with open(latest_file_path, "rb") as file:
                trie = pickle.load(file)
        finally:
            if "ts" in locals() and original_mps_deserialize is not None:
                ts._mps_deserialize = original_mps_deserialize  # type: ignore
                if registry_backup is not None:
                    idx, entry = registry_backup
                    ts._package_registry[idx] = entry  # type: ignore

        return Artifact(latest_file_path, trie)

    def _file_prefix(self, typ: Type) -> str:
        if typ == SubgraphCacheTrie:
            return "trie"
        elif typ == InvertedIndex:
            return "inverted_index"
