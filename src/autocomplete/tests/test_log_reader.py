import os
import random
import string
from contextlib import contextmanager

from autocomplete.log_reader import AnalyticsLogReader

ANALYTICS_LOG_FIXTURE_SEG1 = """
2024-03-29 03:56:49,205 - analytics - INFO - fireplace
2024-03-29 03:56:57,070 - analytics - INFO - floor
2024-03-29 03:56:58,080 - analytics - INFO - floor
2024-03-29 03:57:00,508 - analytics - INFO - garage
2024-03-29 03:57:04,359 - analytics - INFO - kitchen
""".lstrip().encode(
    "utf-8"
)

ANALYTICS_LOG_FIXTURE_SEG2 = """
2024-03-29 03:57:07,420 - analytics - INFO - door
2024-03-29 03:57:11,594 - analytics - INFO - sink
2024-03-29 03:57:14,953 - analytics - INFO - lights
2024-03-29 03:57:18,743 - analytics - INFO - garage
""".lstrip().encode(
    "utf-8"
)


def _random_tmp_file_path() -> str:
    characters = string.ascii_letters + string.digits
    random_string = "".join(random.choice(characters) for _ in range(12))
    return f"/tmp/{random_string}"


@contextmanager
def random_filenames():
    log_file_path = _random_tmp_file_path()
    offset_file_path = _random_tmp_file_path()
    try:
        yield log_file_path, offset_file_path
    finally:
        for file_path in [log_file_path, offset_file_path]:
            if os.path.exists(file_path):
                os.remove(file_path)


def test():
    with random_filenames() as (log_file_path, offset_file_path):
        with open(log_file_path, "wb") as file:
            file.write(ANALYTICS_LOG_FIXTURE_SEG1)

        reader = AnalyticsLogReader(log_file_path, offset_file_path)
        assert reader.unique_count() == dict(
            fireplace=1,
            floor=2,
            garage=1,
            kitchen=1,
        )
        assert reader._get_log_offset() == len(ANALYTICS_LOG_FIXTURE_SEG1)
        assert reader.bytes_read == len(ANALYTICS_LOG_FIXTURE_SEG1)

        with open(log_file_path, "ab") as file:
            file.write(ANALYTICS_LOG_FIXTURE_SEG2)
        expected_log_offset = len(ANALYTICS_LOG_FIXTURE_SEG1) + len(
            ANALYTICS_LOG_FIXTURE_SEG2
        )

        assert reader.unique_count() == dict(
            fireplace=1,
            floor=2,
            garage=2,
            kitchen=1,
            door=1,
            sink=1,
            lights=1,
        )
        assert reader._get_log_offset() == expected_log_offset
        assert reader.bytes_read == len(ANALYTICS_LOG_FIXTURE_SEG2)

        reader.unique_count() == dict()
        assert reader._get_log_offset() == expected_log_offset
        assert reader.bytes_read == 0
