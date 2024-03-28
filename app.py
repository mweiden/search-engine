import json
from flask import Flask, request, render_template_string
from util import setup_analytics_logger, get_latest_trie_pkl, get_index_html

app = Flask(__name__)

# set up the analytics logger
analytics_logger = setup_analytics_logger()

AUTOCOMPLETE_TRIE = get_latest_trie_pkl()

# HTML form
HTML_FORM = get_index_html()

@app.route('/', methods=['GET', 'POST'])
def home():
    query = None
    if request.method == 'POST':
        # Extract the value from the form
        query = request.form['query']
        analytics_logger.info(query)
    # Render the form
    return render_template_string(
        HTML_FORM,
        submission_text=f"Query submitted: {query}" if query else "",
    )

@app.route('/autocomplete', methods=['POST'])
def autocomplete():
    global AUTOCOMPLETE_TRIE
    query = request.get_json()['query']
    if query == "":
        return "[]"
    node = AUTOCOMPLETE_TRIE.find(query)
    suggestions = [] if node is None else node.cache_sorted_keys
    app.logger.info(f"autocomplete suggestions: {suggestions}")
    return json.dumps(suggestions)


@app.route('/load-trie', methods=['POST'])
def load_trie():
    global AUTOCOMPLETE_TRIE
    AUTOCOMPLETE_TRIE = get_latest_trie_pkl()
    return "OK"