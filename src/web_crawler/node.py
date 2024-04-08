import hashlib
from dataclasses import dataclass, field
from urllib.parse import urlparse, urlunparse


@dataclass
class Node:
    raw_url: str
    depth: int = field(default=0)
    title: str | None = field(default=None)
    text: str | None = field(default=None)
    priority: float = field(default=-float("inf"))

    @property
    def id(self) -> str:
        return hashlib.sha1(self.url.encode()).hexdigest()

    @property
    def url(self) -> str:
        # Parse the URL into components
        parsed_url = urlparse(self.raw_url)

        # Reconstruct the URL without the query and fragment
        stripped_url = urlunparse(
            (
                parsed_url.scheme,
                parsed_url.netloc,
                parsed_url.path,
                parsed_url.query,
                parsed_url.params,
                "",  # No fragment
            )
        )
        return stripped_url

    @property
    def netloc(self) -> str:
        return urlparse(self.raw_url).netloc

    # This is a hack to get Node to work with priority queues
    def __lt__(self, other: "Node") -> bool:
        assert self.priority is not None
        assert other.priority is not None
        return self.priority < other.priority
