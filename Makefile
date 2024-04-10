.PHONY: scaffold
scaffold:
	mkdir -p pickles/{autocomplete_tries,inverted_indexes}

.PHONY: install
install:
	python -m pip install --upgrade pip
	python -m pip install -r requirements.txt
	python -m pip install -r requirements-dev.txt

.PHONY: build
build: scaffold
	docker build -t python:flask .

.PHONY: fix
fix:
	black .

.PHONY: lint
lint:
	# stop the build if there are Python syntax errors or undefined names
	flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics
	# exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
	flake8 src/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

.PHONY: test
test:
	pytest src/

.PHONY: inverted_index
inverted_index:
	cd src && python web_crawler_cron.py
	curl -i -XPOST localhost:3000/inverted-index/load
