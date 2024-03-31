import json
import logging
from flask import Flask, request, render_template_string
from util import add_file_handler, add_stream_handler, get_index_html
from trie_storage import TrieStorage

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

analytics_logger = logging.Logger("analytics")
add_file_handler(analytics_logger, "logs/query.log")

HTML_FORM = get_index_html()

TRIE_STORAGE = TrieStorage("pickles")
AUTOCOMPLETE_TRIE = TRIE_STORAGE.get_latest_trie().trie


@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML_FORM)


@app.route("/autocomplete", methods=["POST"])
def autocomplete():
    query = request.get_json()["query"]
    if query == "":
        return json.dumps([])
    node = AUTOCOMPLETE_TRIE.find(query)
    suggestions = [] if node is None else node.cache_sorted_keys
    return json.dumps(suggestions)


@app.route("/submit-query", methods=["POST"])
def submit_query():
    query = request.form["query"]
    analytics_logger.info(query)
    app.logger.info(f"Received query: {query}")
    return "OK"


@app.route("/load-trie", methods=["POST"])
def load_trie():
    global AUTOCOMPLETE_TRIE
    trie_blob = TRIE_STORAGE.get_latest_trie()
    AUTOCOMPLETE_TRIE = trie_blob.trie
    app.logger.info(f"Loaded new trie: {trie_blob.file_path}")
    return "OK"


@app.route("/health", methods=["GET"])
def health():
    return "OK"
