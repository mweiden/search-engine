import pickle
from typing import Dict
from urllib import request

from collections import defaultdict
from datetime import datetime

from subgraph_cache_trie import SubgraphCacheTrie
from util import setup_console_logger

logger = setup_console_logger("log_reader")


def _get_counts_from_query_log() -> Dict[str, int]:
    query_counts = defaultdict(int)
    with open("query.log", "r") as file:
        for line in file:
            query = line.rsplit(" - ", 1)[-1].strip()
            query_counts[query] += 1
    return query_counts


def _create_trie(query_counts: Dict[str, int]) -> SubgraphCacheTrie:
    trie = SubgraphCacheTrie()
    for key, count in query_counts.items():
        trie.insert(key, count)
    return trie


def _save_trie(trie: SubgraphCacheTrie) -> str:
    now = datetime.now()
    formatted_date = now.strftime("%Y%m%d%H%M%S")
    pkl_file_name = f"pickles/trie_{formatted_date}.pkl"
    with open(pkl_file_name, "wb") as file:
        pickle.dump(trie, file)
    return pkl_file_name


def _notify_server() -> int:
    req = request.Request("http://server:3000/load-trie", method="POST")
    with request.urlopen(req) as response:
        status_code = response.status
    return status_code


if __name__ == "__main__":
    # munge the log and generate counts for queries
    query_counts = _get_counts_from_query_log()
    logger.info(f"Collected query counts for {len(query_counts)} distinct queries.")

    # build a trie with subgraph caching for fast access
    trie = _create_trie(query_counts)
    logger.info("SubgraphCacheTrie loaded.")

    # save the trie to a file
    pkl_file_name = _save_trie(trie)
    logger.info(f"SubgraphCacheTrie saved to {pkl_file_name}")

    # tell the server to pick up the the new trie
    logger.info(f"Requesting that server to load trie {pkl_file_name}")
    status_code = _notify_server()
    logger.info(f"Server response for loading {pkl_file_name}: {status_code}")
