import json
from flask import Flask, request, render_template_string
from util import setup_analytics_logger, get_latest_trie_pkl, get_index_html

app = Flask(__name__)
analytics_logger = setup_analytics_logger()
HTML_FORM = get_index_html()
AUTOCOMPLETE_TRIE = get_latest_trie_pkl()


@app.route("/", methods=["GET", "POST"])
def home():
    query = None
    if request.method == "POST":
        query = request.form["query"]
        analytics_logger.info(query)
    return render_template_string(
        HTML_FORM,
        submission_text=f"Query submitted: {query}" if query else "",
    )


@app.route("/autocomplete", methods=["POST"])
def autocomplete():
    query = request.get_json()["query"]
    if query == "":
        return json.dumps([])
    node = AUTOCOMPLETE_TRIE.find(query)
    suggestions = [] if node is None else node.cache_sorted_keys
    return json.dumps(suggestions)


@app.route("/load-trie", methods=["POST"])
def load_trie():
    global AUTOCOMPLETE_TRIE
    AUTOCOMPLETE_TRIE = get_latest_trie_pkl()
    return "OK"
