import sys
import logging
from typing import Dict
from urllib import request

from subgraph_cache_trie import SubgraphCacheTrie
from trie_storage import TrieStorage
from log_reader import AnalyticsLogReader
from util import add_stream_handler

logger = logging.Logger("log_reader")
add_stream_handler(logger)


def _update_trie(trie: SubgraphCacheTrie, query_counts: Dict[str, int]):
    for key, count in query_counts.items():
        trie.insert(key, count)


def _notify_server() -> int:
    req = request.Request("http://server:3000/load-trie", method="POST")
    with request.urlopen(req) as response:
        status_code = response.status
    return status_code


if __name__ == "__main__":
    log_reader = AnalyticsLogReader("query.log", "query_log_offset.txt")
    trie_storage = TrieStorage("pickles")

    # munge the log and generate counts for queries
    query_counts = log_reader.unique_count()
    logger.info(f"Collected query counts for {len(query_counts)} distinct queries.")

    # if nothing new in the log was read, just quit
    if log_reader.bytes_read == 0:
        logger.info("No new log entries found in the log. Skipping trie update.")
        sys.exit(0)

    # build a trie with subgraph caching for fast access
    pkld_trie = trie_storage.get_latest_trie().trie
    trie = pkld_trie if pkld_trie is not None else SubgraphCacheTrie()
    _update_trie(trie, query_counts)
    logger.info("SubgraphCacheTrie loaded.")

    # save the trie to a file
    pkl_file_name = trie_storage.save(trie)
    logger.info(f"SubgraphCacheTrie saved to {pkl_file_name}")

    # tell the server to pick up the the new trie
    status_code = _notify_server()
    logger.info(f"Server response for loading {pkl_file_name}: {status_code}")
