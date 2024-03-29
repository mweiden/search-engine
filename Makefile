.PHONY: scaffold
scaffold:
	mkdir -p pickles

.PHONY: build
build: scaffold
	docker build -t python:flask .
