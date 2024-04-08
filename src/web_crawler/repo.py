import asyncio
import os

from web_crawler.node import Node


class CrawlerStorage:

    def __init__(self, directory):
        self.directory = directory
        if not os.path.exists(self.directory):
            os.mkdir(self.directory)

    def _node_dir(self, node: Node) -> str:
        return f"{self.directory}/{node.id}"

    def exists(self, node: Node) -> bool:
        return os.path.exists(self._node_dir(node))

    async def save(self, node: Node) -> str:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._save, node)

    def _save(self, node: Node) -> str:
        dirname = self._node_dir(node)

        if not self.exists(node):
            os.mkdir(dirname)

        meta_file = f"{dirname}/meta"
        html_file = f"{dirname}/html"

        with open(meta_file, "w") as file:
            file.write(node.url)

        with open(html_file, "w") as file:
            file.write(node.text)
        return dirname
