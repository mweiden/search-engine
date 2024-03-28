import logging
import glob
import pickle

from subgraph_cache_trie import SubgraphCacheNode


def setup_analytics_logger() -> logging.Logger:
    analytics_logger = logging.getLogger("analytics")
    analytics_logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler("query.log")
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    analytics_logger.addHandler(file_handler)
    return analytics_logger


def setup_console_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger


def get_latest_trie_pkl() -> SubgraphCacheNode:
    matching_files = glob.glob("pickles/trie_*.pkl")
    with open(sorted(matching_files)[-1], "rb") as file:
        trie = pickle.load(file)
    return trie


def get_index_html() -> str:
    with open("index.html", "r") as file:
        html = file.read()
    return html
