import json
import logging
from dataclasses import asdict
from flask import Flask, request, render_template_string
from flask_sse import sse

from autocomplete.mermaid import Mermaid
from autocomplete.subgraph_cache_trie import SubgraphCacheTrie
from search.inverted_index import InvertedIndex
from pickle_store import PickleStore
from util import add_file_handler, get_static_file
from env import (
    TRIE_STORAGE_PATH,
    QUERY_LOG_PATH,
    REDIS_URL,
    INVERTED_INDEX_STORAGE_PATH,
)

# Flask application config
app = Flask(__name__)
app.config["REDIS_URL"] = REDIS_URL
app.register_blueprint(sse, url_prefix="/stream")

# logging config
app.logger.setLevel(logging.INFO)
analytics_logger = logging.Logger("analytics")
add_file_handler(analytics_logger, QUERY_LOG_PATH)

# static pages
HTML_HOME = get_static_file("index.html")
HTML_TRIE = get_static_file("trie.html")

# inverted index config
INVERTED_INDEX_STORAGE = PickleStore(INVERTED_INDEX_STORAGE_PATH)
INVERTED_INDEX = INVERTED_INDEX_STORAGE.get_latest(InvertedIndex).artifact

# autocomplete config
TRIE_STORAGE = PickleStore(TRIE_STORAGE_PATH)
try:
    AUTOCOMPLETE_TRIE = TRIE_STORAGE.get_latest(SubgraphCacheTrie).artifact
except AttributeError as e:
    AUTOCOMPLETE_TRIE = SubgraphCacheTrie()
MERMAID = Mermaid()


@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML_HOME)


@app.route("/autocomplete", methods=["POST"])
def autocomplete():
    query = request.get_json()["query"]
    if query == "":
        return json.dumps([])
    node = AUTOCOMPLETE_TRIE.find(query)
    suggestions = [] if node is None else node.cache_sorted_keys
    return suggestions


@app.route("/search", methods=["POST"])
def search():
    query = request.form["query"]
    analytics_logger.info(query)
    app.logger.info(f"Received query: {query}")
    search_results = INVERTED_INDEX.top_k(query)
    return [asdict(result) for result in search_results]


@app.route("/inverted-index/load", methods=["POST"])
def load_inverted_index():
    global INVERTED_INDEX
    inverted_index_blob = INVERTED_INDEX_STORAGE.get_latest(InvertedIndex)
    INVERTED_INDEX = inverted_index_blob.artifact
    app.logger.info(f"Loaded new inverted index: {inverted_index_blob.file_path}")
    return dict(status="OK")


@app.route("/trie", methods=["GET"])
def trie():
    return render_template_string(HTML_TRIE)


@app.route("/trie/load", methods=["POST"])
def load_trie():
    global AUTOCOMPLETE_TRIE
    trie_blob = TRIE_STORAGE.get_latest(SubgraphCacheTrie)
    AUTOCOMPLETE_TRIE = trie_blob.artifact
    app.logger.info(f"Loaded new trie: {trie_blob.file_path}")
    # notify clients to pull the new trie graph
    sse.publish({"event": "new trie!"}, type="content-updates")
    return dict(status="OK")


@app.route("/trie/graph", methods=["GET"])
def trie_graph():
    return dict(data=MERMAID.render_trie(AUTOCOMPLETE_TRIE))


@app.route("/health", methods=["GET"])
def health():
    return dict(status="OK")
