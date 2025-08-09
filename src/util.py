import logging
from urllib import request

LOG_FORMAT = "%(levelname)s:%(name)s:%(asctime)s - %(message)s"


def add_file_handler(logger: logging.Logger, filename: str) -> logging.Logger:
    file_handler = logging.FileHandler(filename)
    formatter = logging.Formatter(LOG_FORMAT)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


def get_static_file(filename: str) -> str:
    with open(f"static/{filename}", "r") as file:
        html = file.read()
    return html


def notify_server(command: str) -> int:
    assert command in set(["trie/load", "inverted-index/load"])
    req = request.Request(f"http://server:3000/{command}", method="POST")
    with request.urlopen(req) as response:
        status_code = response.status
    return status_code
