import time


def current_time_ms() -> int:
    return int(1000 * time.time())
