import os
from typing import Dict, Optional, Tuple, Iterator

from collections import defaultdict


class AnalyticsLogReader:

    def __init__(self, log_file_path: str, log_offset_file_path: str):
        self.log_file_path = log_file_path
        self.log_offset_file_path = log_offset_file_path
        self.bytes_read = 0
        self.counts = defaultdict(int)

    def _get_log_offset(self) -> int:
        if not os.path.exists(self.log_offset_file_path):
            return 0
        with open(self.log_offset_file_path, "r") as file:
            try:
                offset = int(file.read().strip())
            except ValueError:
                offset = 0
        return offset

    def _set_log_offset(self, offset: int):
        with open(self.log_offset_file_path, "w") as file:
            file.write(str(offset))

    def _unread_lines(self, offset: Optional[int]) -> Iterator[Tuple[str, int]]:
        with open(self.log_file_path, "r") as file:
            if offset is not None:
                file.seek(offset)
            while True:
                line = file.readline()
                if not line:
                    break
                yield line, file.tell()

    def unique_count(self) -> Dict[str, int]:
        offset = self._get_log_offset()
        last_offset = offset
        for line, new_offset in self._unread_lines(offset):
            query = line.rsplit(" - ", 1)[-1].strip()
            self.counts[query] += 1
            last_offset = new_offset
        self._set_log_offset(last_offset)
        self.bytes_read = last_offset - offset
        return self.counts
