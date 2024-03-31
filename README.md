# Autocomplete
[![Python package](https://github.com/mweiden/autocomplete/actions/workflows/python-package.yml/badge.svg)](https://github.com/mweiden/autocomplete/actions/workflows/python-package.yml)

Toy example of an autocomplete distributed system.

Components:
1. A web server that serves a simple html page with text input box - on submit the query is logged to an analytics log
1. A cron job that reads the analytics log and constructs a Trie with caching to serve autocomplete suggestions in the text box on the html page

## Running

Prerequisites for running:

* make
* Docker
* A web browser

To run the application

1. `make build`
1. `docker-compose up`
1. Open a browser to `localhost:3000`
1. Start submitting queries

Note: the autosuggest trie is refreshed every 30 seconds.

## Development

Prerequisites for developing:

* Python/Pip

Create a virtual environment

```
python -m venv .venv
```

Install requirements

```
make install
```

Run tests

```
make test
```
