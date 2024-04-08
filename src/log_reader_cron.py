import sys
import logging
from typing import Dict

from autocomplete.subgraph_cache_trie import SubgraphCacheTrie
from pickle_store import PickleStore
from autocomplete.log_reader import AnalyticsLogReader
from util import notify_server
from env import QUERY_LOG_PATH, TRIE_STORAGE_PATH, QUERY_LOG_OFFSET_PATH

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("log_reader")


def _update_trie(trie: SubgraphCacheTrie, query_counts: Dict[str, int]):
    for key, count in query_counts.items():
        trie.insert(key, count)


if __name__ == "__main__":
    log_reader = AnalyticsLogReader(QUERY_LOG_PATH, QUERY_LOG_OFFSET_PATH)
    trie_storage = PickleStore(TRIE_STORAGE_PATH)

    # munge the log and generate counts for queries
    query_counts = log_reader.unique_count()
    logger.info(f"Collected query counts for {len(query_counts)} distinct queries.")

    # if nothing new in the log was read, just quit
    if log_reader.bytes_read == 0:
        logger.info("No new log entries found in the log. Skipping trie update.")
        sys.exit(0)

    # build a trie with subgraph caching for fast access
    pkld_trie = trie_storage.get_latest(SubgraphCacheTrie).artifact
    trie = pkld_trie if pkld_trie is not None else SubgraphCacheTrie()
    _update_trie(trie, query_counts)
    logger.info("SubgraphCacheTrie loaded.")

    # save the trie to a file
    pkl_file_name = trie_storage.save(trie)
    logger.info(f"SubgraphCacheTrie saved to {pkl_file_name}")

    # tell the server to pick up the the new trie
    status_code = notify_server("trie/load")
    logger.info(f"Server response for loading {pkl_file_name}: {status_code}")
