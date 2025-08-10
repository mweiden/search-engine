import os
import pickle
import tempfile

import torch

from pickle_store import PickleStore
from search.inverted_index import InvertedIndex


class Dummy:
    def __init__(self, value: int):
        self.tensor = torch.tensor([value])


def _create_mps_pickle(path: str, obj: Dummy) -> None:
    """Create a pickle file where tensor storage is tagged as 'mps'."""
    with open(path, "wb") as fh:
        pickle.dump(obj, fh)
    data = open(path, "rb").read().replace(b"cpu", b"mps")
    with open(path, "wb") as fh:
        fh.write(data)


def test_get_latest_handles_mps_pickles():
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "inverted_index_19700101000000.pkl")
        _create_mps_pickle(file_path, Dummy(42))
        store = PickleStore(tmpdir)
        artifact = store.get_latest(InvertedIndex)
        assert artifact is not None
        assert artifact.artifact.tensor.item() == 42
