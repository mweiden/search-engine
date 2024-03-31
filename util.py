import logging

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def add_file_handler(logger: logging.Logger, filename: str) -> logging.Logger:
    file_handler = logging.FileHandler(filename)
    formatter = logging.Formatter(LOG_FORMAT)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def add_stream_handler(logger: logging.Logger):
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(LOG_FORMAT)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


def get_index_html() -> str:
    with open("index.html", "r") as file:
        html = file.read()
    return html
