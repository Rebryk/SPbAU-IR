from collections import deque
from urllib.robotparser import RobotFileParser


class Website:
    def __init__(self, scheme: str, hostname: str):
        self.scheme = scheme
        self.hostname = hostname
        self.last_time = 0

        self._urls = set()
        self._queue = deque()

        # parse robots.txt
        self._robot_parser = RobotFileParser()
        self._robot_parser.set_url("{}://{}/robots.txt".format(scheme, hostname))
        self._robot_parser.read()

    def can_fetch(self, user_agent: str, url: str) -> bool:
        return self._robot_parser.can_fetch(user_agent, url)

    def add_url(self, url: str, depth: int = 0):
        if url not in self._urls:
            self._urls.add(url)
            self._queue.append((url, depth))

    def get_url(self) -> (str, int):
        return self._queue.popleft()

    def crawl_delay(self, user_agent: str) -> int:
        return self._robot_parser.crawl_delay(user_agent) * 1000

    def is_empty(self) -> bool:
        return len(self._queue) == 0
